def ms2time(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = str(int(seconds))
    minutes = (millis / (1000 * 60)) % 60
    minutes = str(int(minutes))
    hours = str(int((millis / (1000 * 60 * 60)) % 24))

    if len(minutes) == 1:
        minutes = str("0" + minutes)

    if len(seconds) == 1:
        seconds = str("0" + seconds)

    if hours != "0":
        return f"{hours}:{minutes}:{seconds}"

    return f"{minutes}:{seconds}"
