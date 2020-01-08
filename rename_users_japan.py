#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
#   Copyright (C) 2018 University of Dundee. All rights reserved.
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------------

"""
This script sets the FirstName and LastName for user-1 to user-40
This is the japanese version, where the first ten users have
names of japanese scientists written in japanese signs.
The first ten names are

Katsuko Saruhashi 勝子 猿橋
Yoshinori Ohsumi 良典 大隅
Chika Kuroda チカ 黒田
Shinya Yamanaka 伸弥 山中
Kono Yasui コノ 保井
Yoichiro Nambu 陽一郎 南部
Toshiko Yuasa 年子 湯浅
Fumiko Yonezawa 富美子 米沢
Teruko Ishizaka 照子 石坂
Tsuneko Okazaki 恒子 岡崎

Number 39 in the original list was Yoshinori Ohsumi, written in
latin alphabet signs. Instead, in this list, number 39 is
Charles Darwin. Yoshinori is now number 2 and is written in japanese signs.
"""

import argparse
from omero.rtypes import rstring
from omero.gateway import BlitzGateway


def run(username, password, host, port):

    full_names = ["勝子 猿橋",
                  "良典 大隅",
                  "チカ 黒田",
                  "伸弥 山中",
                  "コノ 保井",
                  "陽一郎 南部",
                  "年子 湯浅",
                  "富美子 米沢",
                  "照子 石坂",
                  "恒子 岡崎",
                  "Louis Pasteur",
                  "Ada Lovelace",
                  "Linus Pauling",
                  "Frances Kelsey",
                  "Maurice Wilkins",
                  "Florence Nightingale",
                  "John Sulston",
                  "Elizabeth Blackwell",
                  "Richard Dawkins",
                  "Caroline Dean",
                  "Stephen Reicher",
                  "Wendy Barclay",
                  "Paul Nurse",
                  "Jennifer Doudna",
                  "Adrian Thomas",
                  "Ann Clarke",
                  "Oswald Avery",
                  "Liz Sockett",
                  "Erwin Chargaff",
                  "Tracey Rogers",
                  "Ronald Fisher",
                  "Rachel Carson",
                  "William Harvey",
                  "Nettie Stevens",
                  "Jeffrey Hall",
                  "Youyou Tu",
                  "Michael Rosbash",
                  "Carol Greider",
                  "Charles Darwin",
                  "Rosalyn Yalow"]

    conn = BlitzGateway(username, password, host=host, port=port)
    try:
        conn.connect()
        admin_service = conn.getAdminService()
        for i, full_name in enumerate(full_names):
            username = 'oki-admin'
            print(username, full_name)
            exp = admin_service.lookupExperimenter(username)
            names = full_name.split(" ")
            exp.firstName = rstring(names[0])
            exp.lastName = rstring(names[1])
            admin_service.updateExperimenter(exp)
    except Exception as exc:
        print("Error while renaming users: %s" % str(exc))
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('--server', default="workshop.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.username, args.password, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
