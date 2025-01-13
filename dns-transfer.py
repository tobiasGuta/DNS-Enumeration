import argparse
import dns.query as dq
import dns.zone as dz

# List of found subdomains
Subdomains = []


# Define the AXFR Function
def AXFR(domain, nameserver):
    """
    Perform a zone transfer for the given domain and nameserver.
    If successful, subdomains will be added to the global Subdomains list.
    If there is an error, the error message will be displayed.
    """
    try:
        # Try to perform the zone transfer
        axfr = dz.from_xfr(dq.xfr(nameserver, domain))

        # If zone transfer is successful
        if axfr:
            print(f'[*] Successful Zone Transfer from {nameserver}')

            # Add found subdomains to the global Subdomains list
            for record in axfr:
                subdomain = f'{record.to_text()}.{domain}'
                Subdomains.append(subdomain)
                print(f'Found subdomain: {subdomain}')

    except Exception as error:
        # If zone transfer fails, print the error
        print(f"Error: {error}")
        pass


# Main execution with argparse
if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Perform a DNS zone transfer and retrieve subdomains.")
    parser.add_argument("domain", help="The domain name for which to perform the zone transfer.")
    parser.add_argument("nameservers", nargs='+', help="One or more nameservers to use for the zone transfer.")

    # Parse the command-line arguments
    args = parser.parse_args()

    # For each nameserver, try to perform the zone transfer
    for nameserver in args.nameservers:
        AXFR(args.domain, nameserver)

    # Print the list of found subdomains
    print('\nAll found subdomains:')
    for subdomain in Subdomains:
        print(subdomain)
