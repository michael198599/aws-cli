# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import logging

from awscli.customizations.s3.syncstrategy.base import BaseSync


LOG = logging.getLogger(__name__)


EXACT_TIMESTAMPS = {'name': 'exact-timestamps', 'action': 'store_true',
                    'help_text': (
                        'When syncing from S3 to local, same-sized '
                        'items will be ignored only when the timestamps '
                        'match exactly. The default behavior is to ignore '
                        'same-sized items unless the local version is newer '
                        'than the S3 version.')}


class ExactTimestampsSync(BaseSync):

    ARGUMENT = EXACT_TIMESTAMPS

    def determine_should_sync(self, src_file, dest_file):
        same_size = self.compare_size(src_file, dest_file)
        same_last_modified_time = self.compare_time(src_file, dest_file)
        should_sync = (not same_size) or (not same_last_modified_time)
        if should_sync:
            LOG.debug("syncing: %s -> %s, size_changed: %s, "
                      "last_modified_time_changed: %s",
                      src_file.src, src_file.dest,
                      not same_size, not same_last_modified_time)
        return should_sync

    def compare_time(self, src_file, dest_file):
        src_time = src_file.last_update
        dest_time = dest_file.last_update
        delta = dest_time - src_time
        cmd = src_file.operation_name
        if cmd == 'download':
            return self.total_seconds(delta) == 0
        else:
            return super(SizeOnlySyncStrategy, self).compare_time(src_file,
                                                                  dest_file)
