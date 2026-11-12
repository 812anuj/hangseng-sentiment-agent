from app.config.settings import settings


def main():

    print("=" * 55)
    print(settings.PROJECT_NAME)
    print("=" * 55)

    print("Project configuration loaded successfully!")

    print("\nConfiguration:")

    print(f"Project: {settings.PROJECT_NAME}")
    print(f"Debug Mode: {settings.DEBUG}")

    # Check API credentials without exposing them
    print(
        "Apify API configured:",
        bool(settings.APIFY_API_TOKEN)
    )

    print(
        "Exa API configured:",
        bool(settings.EXA_API_KEY)
    )

    print("\nApplication started successfully!")


if __name__ == "__main__":
    main()