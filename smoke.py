"""Make one real Sarvam chat call after the user supplies an API key."""

import os

from app import load_dotenv


def main():
    load_dotenv()
    if not os.environ.get("SARVAM_API_KEY", "").strip():
        raise SystemExit("Set SARVAM_API_KEY in .env before running this smoke call.")

    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[{"role": "user", "content": "Reply with: Notice2Action is ready."}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
