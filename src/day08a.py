from fileinput import FileInput

if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    sum: int = 0

    for line in input:
        _, _, outputs = line.strip().partition(" | ")
        for word in outputs.split():
            if len(word) in {2, 3, 4, 7}:
                sum += 1

    print(sum)
