def info_logging(job: str, message: str) -> str:
    """
    Logs an informational message.

    Args:
        job (str): The job or category of the message.
        message (str): The message to log.
    """
    return f"[{job}] - {message}"