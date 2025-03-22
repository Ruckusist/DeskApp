import argparse
import deskapp


def main():
    parser = argparse.ArgumentParser(
                    prog='Deskapp',
                    description='A text based UI framework for Python.',
                    epilog='Another Ruckusist.com Project.')
    
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()