# DNS Zone Transfer Tool

A simple and effective Python script to perform DNS zone transfers (AXFR) for subdomain enumeration. This tool queries specified nameservers for a target domain and retrieves the zone data to identify subdomains. It supports parallel zone transfer requests, automatic retries on failure, and outputs results in various formats such as plain text, CSV, or JSON for easy processing.

This tool is based on one of the modules from HackTheBox Academy, with several modifications and improvements added to enhance its functionality, speed, and flexibility.

## Features:
- Perform DNS zone transfer (AXFR) against multiple nameservers.
- Supports parallel execution for faster subdomain enumeration.
- Retry mechanism for temporary network failures.
- Output results in text, CSV, or JSON formats.
- Easy-to-use command-line interface with flexible options.

## Requirements:
- `dnspython`
- `tqdm` (for progress bar)
