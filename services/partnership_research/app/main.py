from services.partnership_research.app.services.leads import score_lead


async def run_demo() -> dict[str, object]:
    return score_lead(
        {
            "title": "Healthy habits daily",
            "description": "Nutrition and lifestyle content for Russian-speaking users",
        }
    )


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(run_demo()))
