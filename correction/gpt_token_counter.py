import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens(string, model = "gpt-3.5-turbo"):

    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))

    return num_tokens

if __name__ == "__main__":
    print(num_tokens("hi this is a big, test?"))
