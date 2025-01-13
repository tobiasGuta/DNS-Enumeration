#!/usr/bin/env python3

# Dependencies:
# python3-dnspython
# tqdm (for progress bar)
# concurrent.futures (for parallelization)
# csv and json for structured output

import dns.zone as dz
import dns.query as dq
import dns.resolver as dr
import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import json
import csv
from tqdm import tqdm


# Initialize Resolver-Class from dns.resolver as "NS"
NS = dr.Resolver()

# List of found subdomains
subdomains = []

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# Define the AXFR Function with retries
def axfr(domain, nameserver, retries=3, backoff=2):
    """
    Attempt a zone transfer for the given domain and nameserver with retries in case of failure.
    """
    attempt = 0
    while attempt < retries:
        try:
            # Perform the zone transfer
            axfr_response = dz.from_xfr(dq.xfr(nameserver, domain))
            if axfr_response:
                logging.info(f'Successful Zone Transfer from {nameserver}')
                for record in axfr_response:
                    subdomains.append(f'{record.to_text()}.{domain}')
            break  # Exit the loop if successful
        except Exception as error:
            logging.error(f"Error with nameserver {nameserver}: {error}")
            attempt += 1
            if attempt < retries:
                logging.info(f"Retrying... Attempt {attempt + 1}")
                time.sleep(backoff ** attempt)  # Exponential backoff


# Function to save results in structured formats
def save_results(subdomains, output_file, output_format):
    unique_subdomains = set(subdomains)  # Remove duplicates
    
    if output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(list(unique_subdomains), f, indent=4)
        logging.info(f"Results saved to {output_file} in JSON format.")
    
    elif output_format == 'csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Subdomain'])
            for subdomain in unique_subdomains:
                writer.writerow([subdomain])
        logging.info(f"Results saved to {output_file} in CSV format.")
    
    else:
        # Default to plain text if no specific format is chosen
        with open(output_file, 'w') as f:
            for subdomain in unique_subdomains:
                f.write(f"{subdomain}\n")
        logging.info(f"Results saved to {output_file} in TXT format.")


# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="DNS Zone Transfer Script for Pentesters")
    parser.add_argument('-d', '--domain', type=str, help="Target domain for zone transfer", required=True)
    parser.add_argument('-n', '--nameservers', nargs='+', help="Custom nameservers to query", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output file to save the results", required=True)
    parser.add_argument('-f', '--format', type=str, choices=['json', 'csv', 'txt'], default='txt', 
                        help="Output format: json, csv, or txt (default: txt)")
    return parser.parse_args()


# Main function
if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Override domain and nameservers if specified by user
    DOMAIN = args.domain
    NS.nameservers = args.nameservers

    # Use ThreadPoolExecutor to handle multiple nameservers concurrently
    with ThreadPoolExecutor(max_workers=len(NS.nameservers)) as executor:
        # Use tqdm for progress bar visualization
        list(tqdm(executor.map(lambda ns: axfr(DOMAIN, ns), NS.nameservers), total=len(NS.nameservers), desc="Performing Zone Transfers"))

    # Save the results in the requested format (CSV, JSON, or TXT)
    save_results(subdomains, args.output, args.format)

    # Print results and total count to console
    unique_subdomains = set(subdomains)
    if unique_subdomains:
        logging.info('-------- Found Subdomains:')
        for subdomain in unique_subdomains:
            print(subdomain)
        print(f"\nTotal unique subdomains found: {len(unique_subdomains)}")
    else:
        logging.info('No subdomains found.')
