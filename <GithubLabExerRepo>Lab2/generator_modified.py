import random

def getWords(filename):
    """
    Reads words from a file and returns them as a tuple.

    :param filename: Name of the file containing words.
    :return: A tuple of words.
    """
    try:
        with open(filename, 'r') as file:
            words = [line.strip().upper() for line in file if line.strip()]
        return tuple(words)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return ()

# Initialize vocabulary from files
articles = getWords("articles.txt")
nouns = getWords("nouns.txt")
verbs = getWords("verbs.txt")
prepositions = getWords("prepositions.txt")

def sentence():
    """Builds and returns a sentence."""
    return nounPhrase() + " " + verbPhrase()

def nounPhrase():
    """Builds and returns a noun phrase."""
    return random.choice(articles) + " " + random.choice(nouns)

def verbPhrase():
    """Builds and returns a verb phrase."""
    return random.choice(verbs) + " " + nounPhrase() + " " + \
           prepositionalPhrase()

def prepositionalPhrase():
    """Builds and returns a prepositional phrase."""
    return random.choice(prepositions) + " " + nounPhrase()

def main():
    """Allows the user to input the number of sentences to generate."""
    if not (articles and nouns and verbs and prepositions):
        print("Error: Vocabulary files are missing or empty.")
        return

    try:
        number = int(input("Enter the number of sentences: "))
        for count in range(number):
            print(sentence())
    except ValueError:
        print("Error: Please enter a valid number.")

# The entry point for program execution
if __name__ == "__main__":
    main()
