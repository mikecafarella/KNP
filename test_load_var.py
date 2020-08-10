import kgpl


if __name__ == "__main__":
    var = kgpl.load_var(1)
    print(var.val_id)
    print(type(var.val_id))
    val = kgpl.load_val(var.val_id)
    print(type(val.val))

