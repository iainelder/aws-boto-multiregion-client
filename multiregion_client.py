class MultiRegionClient(object):

    def __init__(self, session, service_name, regions):

        self._clients = {
            r: session.client(service_name, region_name=r)
            for r in regions
        }

        self._methods = list(self._clients.values())[0].meta.method_to_api_mapping


    def __getattr__(self, name):

        if name in self._methods:
            return self._build_dispatcher_with_region_at_top_level(name)

        # I'm not sure why I have to write this explicitly. How do I defer to object's default handling?
        # I got this from the question text of https://stackoverflow.com/questions/50542177/correct-handling-of-attributeerror-in-getattr-when-using-property
        raise AttributeError(f"{type(self).__name__} object has no attribute {name}")


    def _build_dispatcher_with_region_at_top_level(self, method):

        def dispatch(*args, **kwargs):

            return {
                r: c.__getattribute__(method)(*args, **kwargs)
                for r, c in self._clients.items()
            }

        return dispatch


    def _build_dispatcher_with_request_region_in_each_item(self, method):
        """
        FIXME: The idea of this method is to return a dispatch that returns the same shape as a normal client except that every resource has a RequestRegion key.

        Each AWS operation has its own shape, so doing this in the general case would require inspecting each operation model. Check the output of dump_operation_members.py for the all the cases that have to be handled.

        Currently RequestRegion is merged into the ResponseMetadata dict, but I'm not evne sure that's the right way to do it for this object. If you care about the ResponseMetadata for a region, it would be easier to look it up by key instead of filtering a list.
        """

        def dispatch(*args, **kwargs):

            dispatch = self._build_dispatcher_with_region_at_top_level(method)
            result = dispatch(*args, **kwargs)

            return {
                "ResponseMetadata": [
                    {**v["ResponseMetadata"], **{"RequestRegion": k}}
                    for k, v in result.items()
                ]
            }

        return dispatch
