def log(content: str, print_content: bool = True):
    if print_content:
        print(content)
    with open("nbmake.log", "a+") as f:
        f.write("\n")
        f.write(content)
