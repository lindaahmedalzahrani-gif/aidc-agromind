"""
AgroMind RAG - Interactive Application
"""

import sys
from app.rag import initialize_rag, ask_rag


def interactive_mode(rag):
    print("\n" + "=" * 60)
    print("AgroMind RAG - Interactive Mode")
    print("=" * 60)
    print("\nType your question in English or Chinese.")
    print("Example: 'How to treat Rice from Late Blight?'")
    print("Example: '如何处理水稻晚疫病?'")
    print("\nType 'exit' to quit.\n")

    while True:
        try:
            question = input("\nQuestion: ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit']:
                print("\nGoodbye.")
                break

            ask_rag(rag, question)

        except KeyboardInterrupt:
            print("\n\nStopped.")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    try:
        rag = initialize_rag()

        if len(sys.argv) > 1:
            question = " ".join(sys.argv[1:])
            ask_rag(rag, question)
        else:
            interactive_mode(rag)

    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
