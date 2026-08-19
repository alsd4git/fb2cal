from .errors import GraphQLSchemaError
from .facebook_user import FacebookUser


class Transformer:

    def transform_birthday_comet_monthly_to_birthdays(self, birthday_comet_root_json):
        """Transform BirthdayCometMonthlyBirthdaysRefetchQuery into contacts."""

        try:
            edges = birthday_comet_root_json['data']['viewer']['all_friends_by_birthday_month']['edges']
        except (KeyError, TypeError) as exc:
            raise GraphQLSchemaError(
                "Facebook birthday response is missing all_friends_by_birthday_month.edges"
            ) from exc
        if not isinstance(edges, list):
            raise GraphQLSchemaError("Facebook birthday edges is not a list")

        facebook_users = []

        try:
            for all_friends_by_birthday_month_edge in edges:
                for friend_edge in all_friends_by_birthday_month_edge['node']['friends']['edges']:
                    friend = friend_edge['node']
                    birthdate = friend['birthdate']
                    picture = friend.get('profile_picture') or {}

                    facebook_users.append(
                        FacebookUser(
                            friend["id"],
                            friend["name"],
                            friend.get("profile_url"),
                            picture.get("uri"),
                            birthdate["day"],
                            birthdate["month"],
                            birthdate.get("year"),
                        )
                    )
        except (KeyError, TypeError) as exc:
            raise GraphQLSchemaError("Facebook birthday response has an unexpected friend schema") from exc

        return facebook_users
