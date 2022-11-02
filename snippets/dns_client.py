#! python3
import sys
import dns.resolver


def info(msg):
    print(f"{sys.argv[0]} [-r] [-t type] hostname")
    sys.exit(msg)


def main():
    args = sys.argv[1:]
    hostname = ""
    rdtype = "A"
    rd = False

    while(args):
        arg = args.pop(0)
        if arg[0] == '-':
            if arg[1] == 'h':
                info(0)
            elif arg[1] == 't':
                rdtype = args.pop(0)
            elif arg[1] == 'r':
                rd = True
            else:
                info(1)
        hostname = arg

    print(f"Name requested: {hostname}")
    resolver = dns.resolver.get_default_resolver()
    if rd:
        resolver.set_flags(dns.flags.RD)
    answers = resolver.resolve(hostname, rdtype, search=rd)
    for rdata in answers:
        print(rdata)


if __name__ == "__main__":
    main()
