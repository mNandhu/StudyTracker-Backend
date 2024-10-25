from crewai_tools import BaseTool


class CustomCalenderTool(BaseTool):
    name: str = "Calender Tool"
    description: str = (
        "This tool can be used to retrieve the academic calendar of current year. The argument"
        "passed is the date for which the calendar is requested."
    )

    def _run(self, argument: str) -> str:
        # Implementation goes here
        raise AssertionError("This function is called!")
        print("This function is called")
        return f"{argument} : 'Working Day' "
