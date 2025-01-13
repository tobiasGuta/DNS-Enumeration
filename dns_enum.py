#!/usr/bin/env python3

# Dependencies:
# python3-dnspython

# Used Modules:
import dns.zone as dz
import dns.query as dq
import dns.resolver as dr
import argparse

# Initialize Resolver-Class from dns.resolver as "NS"
NS = dr.Resolver()

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="DNS Enumeration Tool")
    parser.add_argument("-d", "--domain", required=True, help="Target domain for enumeration")
    parser.add_argument("-n", "--nameservers", nargs="+", help="List of nameservers to query", default=['ns1.example.com', 'ns2.example.com'])
    parser.add_argument("-s", "--subdomains", nargs="+", help="List of common subdomains to check", default=['www', 'mail', 'ftp', 'test', 'dev'])
    return parser.parse_args()

# Perform DNS Query for common subdomains
def query_subdomains(domain, subdomains, resolver):
    found_subdomains = []
    for subdomain in subdomains:
        fqdn = f"{subdomain}.{domain}"
        try:
            answers = resolver.resolve(fqdn, "A")
            for rdata in answers:
                print(f"Found subdomain: {fqdn} -> {rdata.address}")
                found_subdomains.append(fqdn)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass  # No result or domain doesn't exist
    return found_subdomains

# Perform Zone Transfer (AXFR)
def perform_zone_transfer(domain, nameservers):
    for ns in nameservers:
        try:
            print(f"Attempting Zone Transfer to {ns}...")
            zone = dz.from_xfr(dq.xfr(ns, domain))
            for name, node in zone.nodes.items():
                print(f"Zone record: {name.to_text()} -> {node.to_text(zone.origin)}")
        except Exception as e:
            print(f"Zone transfer failed: {e}")

def main():
    # Parse arguments
    args = parse_arguments()

    # Target domain from arguments
    domain = args.domain
    nameservers = args.nameservers
    subdomains = args.subdomains

    # Set the nameservers in the resolver
    NS.nameservers = nameservers

    # Start DNS enumeration
    print(f"Starting DNS Enumeration for {domain}...\n")
    found_subdomains = query_subdomains(domain, subdomains, NS)

    if not found_subdomains:
        print("No subdomains found using standard queries.")

    # Attempt a zone transfer
    perform_zone_transfer(domain, nameservers)

if __name__ == "__main__":
    main()
