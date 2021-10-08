from kgpl_client import kgpl

def main():
    a = kgpl.value(42,"value comment 0","Tiramisu")
    b = kgpl.variable(a,"variable comment 0","Tiramisu")

if __name__ == "__main__":
    main()