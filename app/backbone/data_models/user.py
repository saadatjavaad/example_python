from backbone.mixins.tortoise import (
    TortoiseMixinBase,
    TortoiseMixinContactAtLeastOne,
    TortoiseMixinUserUsername,
)


class UserDataModel(
    TortoiseMixinBase, TortoiseMixinUserUsername, TortoiseMixinContactAtLeastOne
):

    class Meta:
        constraints = [
            "CHECK (phone IS NOT NULL OR email IS NOT NULL)"  # یا شماره یا ایمیل
        ]
