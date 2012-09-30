class MeetupAPIError(Exception):
    def __init__(self, error, *args, **kwargs):
        super(MeetupAPIError, self).__init__(error, *args, **kwargs)
        self.error = error

    def __str__(self):
        return self.error.get("problem", "")


def validated(results):
    """
    Validate Meetup API results, converting error objects into exceptions.

    """

    if "problem" in results.data:
        raise MeetupAPIError(results.data)
    return results


class Meetup(object):

    ENDPOINTS = {
        "events" : "/2/events/",
        "groups" : "/2/groups/",
        "venues" : "/2/venues/",
    }

    def __init__(self, oauth):
        self.oauth = oauth

    def get(self, *args, **kwargs):
        headers = kwargs.setdefault("headers", {})
        headers.setdefault("Accept-Charset", "utf-8")
        return validated(self.oauth.get(*args, **kwargs))

    def get_results(self, endpoint, *args, **kwargs):
        """
        Get all the results for an API query by following each ``next`` link.

        """

        while endpoint:
            data = self.get(endpoint, *args, **kwargs).data

            for result in data["results"]:
                yield result

            endpoint = data["meta"]["next"]

    def groups(self, member_id, fields=(), page=200):
        """
        Retrieve the list of groups for the given member.

        """

        fields = ",".join(fields)
        return self.get_results(
            self.ENDPOINTS["groups"],
            data=[("member_id", member_id), ("fields", fields), ("page", page)]
        )

    def venues(self, group_ids, fields=(), page=200):
        """
        Retrieve the list of venues for the given group ids.

        """

        group_ids = ",".join(str(group_id) for group_id in group_ids)
        fields = ",".join(fields)
        return self.get_results(
            self.ENDPOINTS["venues"],
            data=[("group_id", group_ids), ("fields", fields), ("page", page)]
        )

    def events(self, group_ids, status=(), fields=(), page=200):
        """
        Retrieve the list of events for the given group ids.

        """

        group_ids = ",".join(str(group_id) for group_id in group_ids)
        status = ",".join(status)
        fields = ",".join(fields)
        return self.get_results(
            self.ENDPOINTS["events"], data=[
                ("group_id", group_ids),
                ("status", status),
                ("fields", fields),
                ("page", page)]
        )
