# -*- coding: utf-8 -*-
# Copyright 2016 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from collections import defaultdict

from quodlibet import config
from quodlibet.browsers.soundcloud.api import SoundcloudApiClient
from quodlibet.browsers.soundcloud.library import SoundcloudLibrary, \
    SoundcloudFile
from tests import TestCase

TRACK_ID = 1234


class TSoundcloudFile(TestCase):
    class FakeClient(SoundcloudApiClient):

        def __init__(self):
            super(TSoundcloudFile.FakeClient, self).__init__()
            self.online = True
            self.favoritings = defaultdict(int)
            self.unfavoritings = defaultdict(int)

        def _on_favorited(self, json):
            super(TSoundcloudFile.FakeClient, self)._on_favorited(json)

        def put_favorite(self, track_id):
            self.favoritings[track_id] += 1

        def remove_favorite(self, track_id):
            self.unfavoritings[track_id] += 1

    @classmethod
    def setUpClass(cls):
        config.RATINGS = config.HardCodedRatingsPrefs()

    def setUp(self):
        SoundcloudLibrary.librarian = None
        self.client = self.FakeClient()

    def test_favoriting(self):
        cl = self.client
        song = SoundcloudFile("http://uri", TRACK_ID, False, cl)
        self.failIf(song.has_rating)
        song['~#rating'] = 1.0
        self.failUnless(song.has_rating)
        self.failUnlessEqual(song("~#rating"), 1.0)
        song.write()
        self.failUnless(song.favorite)
        self.failUnlessEqual(cl.favoritings[TRACK_ID], 1)
        self.failUnlessEqual(cl.unfavoritings[TRACK_ID], 0)
        song.write()
        self.failUnlessEqual(cl.favoritings[TRACK_ID], 1)

    def test_unfavoriting(self):
        cl = self.client
        song = SoundcloudFile("http://uri", TRACK_ID, True, cl)
        self.failUnless(song.has_rating)
        self.failUnlessEqual(song("~#rating"), 1.0)
        song['~#rating'] = 0.2
        song.write()
        self.failIf(song.favorite)
        self.failUnlessEqual(cl.unfavoritings[TRACK_ID], 1)
        self.failUnlessEqual(cl.favoritings[TRACK_ID], 0)
        song.write()
        self.failUnlessEqual(cl.unfavoritings[TRACK_ID], 1)
