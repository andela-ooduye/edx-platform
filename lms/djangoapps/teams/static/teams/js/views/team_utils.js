/*  Team utility methods*/
;(function(define) {
    'use strict';
    define(['jquery', 'underscore', 'edx-ui-toolkit/js/utils/string-utils'
    ], function($, _, StringUtils) {
        return {

            /**
             * Convert a 2d array to an object equivalent with an additional blank element
             *
             * @param {Array.<Array.<string>>} options Two dimensional options array
             * @returns {Object} Hash version of the input array
             * @example selectorOptionsArrayToHashWithBlank([["a", "alpha"],["b","beta"]])
             * // returns {"a":"alpha", "b":"beta", "":""}
             */
            selectorOptionsArrayToHashWithBlank: function(options) {
                var map = _.object(options);
                map[''] = '';
                return map;
            },

            teamCapacityText: function(memberCount, maxMemberCount) {
                return StringUtils.interpolate(
                    // Translators: The following message displays the number of members on a team.
                    ngettext(
                        '{memberCount} / {maxMemberCount} Member',
                        '{memberCount} / {maxMemberCount} Members',
                        maxMemberCount
                    ),
                    {memberCount: memberCount, maxMemberCount: maxMemberCount}
                );
            },

            isUserMemberOfTeam: function(memberships, requestUsername) {
                return _.isObject(
                    _.find(memberships, function(membership) {
                        return membership.user.username === requestUsername;
                    })
                );
            },

            hideMessage: function() {
                $('#teams-message').addClass('.is-hidden');
            },

            showMessage: function(message, type) {
                var $message = $('#teams-message');
                if (_.isUndefined(type)) {
                    type = 'warning';
                }
                $message.removeClass('is-hidden').addClass(type);
                $('.teams-content .msg-content .copy').text(message);
                $message.focus();
            },

            /**
             * Parse `data` and show user message. If parsing fails than show `genericErrorMessage`
             */
            parseAndShowMessage: function(data, genericErrorMessage, type) {
                var errors;
                try {
                    errors = JSON.parse(data.responseText);
                    this.showMessage(
                        _.isUndefined(errors.user_message) ? genericErrorMessage : errors.user_message, type
                    );
                } catch (error) {
                    this.showMessage(genericErrorMessage, type);
                }
            }
        };
    });

}).call(this, define || RequireJS.define);
