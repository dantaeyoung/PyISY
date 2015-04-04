from VarEvents import Property


class Group(object):

    """
    Group class

    DESCRIPTION:
        This class interacts with ISY groups (scenes).

    ATTRIBUTES:
        parent: The nodes class
        noupdate: stops automatic updating after manipulation
        status: The status of the node

    METHODS:
        off()
        on()
    """

    status = Property(0)

    def __init__(self, parent, nid, members=[]):
        self.parent = parent
        self._id = nid
        self._members = members
        self.dimmable = False
        self._running = False

        # listen for changes in children
        self._membersHandlers = [ \
                self.parent[m].status.subscribe('changed', self.update) \
                for m in self.members]

        # get and update the status
        self.update()

        # respond to non-silent changes in status
        self.status.reporter = self.__report_status__

    def __del__(self):
        for handler in self._membersHandlers:
            handler.unsubscribe()

    def __str__(self):
        return 'Group(' + self._id + ')'

    def __report_status__(self, new_val):
        # first clean the status input
        if self.status > 0:
            clean_status = 255
        elif self.status <= 0:
            clean_status = 0
        if self.status != clean_status:
            self.status.update(clean_status, force=True, silent=True)

        # now update the nodes
        if clean_status > 0:
            self.on()
        else:
            self.off()

    @property
    def members(self):
        return self._members

    def update(self, e=None):
        for m in self.members:
            if self.parent[m].status > 0:
                self.status.update(255, force=True, silent=True)
                return
        self.status.update(0, force=True, silent=True)

    def off(self):
        """Turns off all the nodes in a scene."""
        response = self.parent.parent.conn.nodeOff(self._id)

        if response is None:
            self.parent.parent.log.warning('ISY could not turn off scene: ' +
                                           self._id)
        else:
            self.parent.parent.log.info('ISY turned off scene: ' + self._id)

    def on(self):
        """Turns on all the nodes in the scene to the set values."""
        response = self.parent.parent.conn.nodeOn(self._id, None)

        if response is None:
            self.parent.parent.log.warning('ISY could not turn on scene: ' +
                                           self._id)
        else:
            self.parent.parent.log.info('ISY turned on scene: ' + self._id)
