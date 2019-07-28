#!/usr/bin/env python

"""Module that is used for getting information
about the (MLB) league and the teams in it.
"""

from __future__ import print_function

import mlbgame.data
import mlbgame.object

from datetime import datetime
import json
import lxml.etree as etree


def __get_league_object():
    """Returns the xml object corresponding to the league

    Only designed for internal use"""
    # get data
    data = mlbgame.data.get_properties()
    # return league object
    #return etree.fromstring(data).getroot().find('leagues').find('league')
    return etree.fromstring(data).find('leagues').find('league')


def league_info():
    """Returns a dictionary of league information"""
    league = __get_league_object()
    output = {}
    for x in league.attrib:
        output[x] = league.attrib[x]
    return output


def team_info():
    """Returns a list of team information dictionaries"""
    teams = __get_league_object().find('teams').findall('team')
    output = []
    for team in teams:
        info = {}
        for x in team.attrib:
            info[x] = team.attrib[x]
        output.append(info)
    return output


def important_dates(year):
    """Returns a dictionary of important dates"""
    output = {}
    data = mlbgame.data.get_important_dates(year)
    #important_dates = etree.fromstring(data).getroot().\
    #    find('queryResults').find('row')
    important_dates = etree.fromstring(data).\
        find('queryResults').find('row')
    try:
        for x in important_dates.attrib:
            output[x] = important_dates.attrib[x]
    except AttributeError:
        raise ValueError('Unable to find important dates for {}.'.format(year))
    return output


def broadcast_info(team_id, date=datetime.now()):
    """Returns a dictionary of broadcast information
    for a given team during a given season"""
    year = date.year
    game_date = date.strftime('%Y-%m-%dT00:00:00')
    data = mlbgame.data.get_broadcast_info(team_id, year)
    schedule = json.loads(data.decode('utf-8'))
    schedule = schedule['mlb_broadcast_info']['queryResults']['row']
    return [g for g in schedule if g['game_date'] == game_date]


class BroadcastInfo(mlbgame.object.Object):
    """Holds broadcast information for a given team and game date
    Properties:
        away_team_id
        home_team_short
        game_time_local
        game_time_home
        source_id
        home_team_full
        game_date
        source_type
        foreign_language
        game_pk
        game_time_away
        game_day
        source_comment
        source_desc
        away_team_abbrev
        away_team_full
        game_id
        home_team_abbrev
        home_team_id
        sort_order
        game_time_et
        away_team_short
        home_away
    """
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def nice_output(self):
        bcast_strs = []
        watch_listen = 'Watch' if self.source_type == 'TV' else 'Listen'
        bcast_strs.append('{}: {} - {}'.format(watch_listen,
                                               self.home_team_full,
                                               self.source_desc))
        bcast_strs.append('{}: {} - {}'.format(watch_listen,
                                               self.away_team_full,
                                               self.source_desc))
        return '\n'.join(bcast_strs)

    def __str__(self):
        return self.nice_output()


class ImportantDates(mlbgame.object.Object):
    """Holds information about important MLB dates and other info.
    Properties:
        all_star_date
        all_star_sw
        file_code
        first_date_2ndh
        first_date_seas
        games
        games_1sth
        games_2ndh
        last_date_1sth
        last_date_seas
        name_abbrev
        name_full
        name_short
        org_code
        org_type
        organization_id
        parent_abbrev
        parent_org
        playoff_games
        playoff_points_sw
        playoff_rounds
        playoff_sw
        playoff_teams
        playoffs_end_date
        playoffs_start_date
        point_values
        split_season_sw
        wildcard_sw
        wildcard_teams
        year
"""
    def nice_output(self):
        """Return a string for printing"""
        dates = [
            str_format('Opening Day {0}: {1}.',
                       [self.year, date_format(self.first_date_seas)]),
            str_format('Last day of the 1st half: {0}.',
                       [date_format(self.last_date_1sth)]),
            str_format('{0} All Star Game: {1}.',
                       [self.year, date_format(self.all_star_date)]),
            str_format('First day of the 2nd half: {}.',
                       [date_format(self.first_date_2ndh)]),
            str_format('Last day of the {0} season: {1}.',
                       [self.year, date_format(self.last_date_seas)]),
            str_format('{0} Playoffs start: {1}.',
                       [self.year, date_format(self.playoffs_start_date)]),
            str_format('{0} Playoffs end: {1}.',
                       [self.year, date_format(self.playoffs_end_date)])
        ]
        return '\n'.join(dates)

    def __str__(self):
        return self.nice_output()


def date_format(my_date):
    try:
        my_date = datetime.strptime(my_date, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return ''
    return my_date.strftime('%A, %B %d')


def str_format(my_str, args):
    return my_str.format(*args)


class Info(mlbgame.object.Object):
    """Holds information about the league or teams

    Properties:
        address
        aws_club_slug
        city
        club
        club_common_name
        club_common_url
        club_full_name
        club_id
        club_spanish_name
        country
        dc_site
        display_code
        division
        es_track_code
        esp_common_name
        esp_common_url
        facebook
        facebook_es
        fanphotos_url
        fb_app_id
        field
        google_tag_manager
        googleplus_id
        historical_team_code
        id
        instagram
        instagram_id
        league
        location
        medianet_id
        mobile_es_url
        mobile_short_code
        mobile_url
        mobile_url_base
        name_display_long
        name_display_short
        newsletter_category_id
        newsletter_group_id
        phone
        photostore_url
        pinterest
        pinterest_verification
        pressbox_title
        pressbox_url
        primary
        primary_link
        postal_code
        secondary
        shop_entry_code
        snapchat
        snapchat_es
        state_province
        team_code
        team_id
        tertiary
        timezone
        track_code
        track_code_dev
        track_filter
        tumblr
        twitter
        twitter_es
        url_cache
        url_esp
        url_prod
        venue_id
        vine
        youtube
    """

    def nice_output(self):
        """Return a string for printing"""
        return '{0} ({1})'.format(self.club_full_name, self.club.upper())

    def __str__(self):
        return self.nice_output()


def roster(team_id):
    """Returns a dictionary of roster information for team id"""
    data = mlbgame.data.get_roster(team_id)
    parsed = json.loads(data.decode('utf-8'))
    players = parsed['roster_40']['queryResults']['row']
    return {'players': players, 'team_id': team_id}


class Roster(object):
    """Represents an MLB Team

    Properties:
        players
        team_id
    """

    def __init__(self, data):
        """Creates a roster object to match info in `data`.

        `data` should be a dictionary of values.
        """
        self.team_id = data['team_id']
        self.players = []
        for player in data['players']:
            self.players.append(Player(player))


class Player(mlbgame.object.Object):
    """Represents an MLB Player

    Properties:
        bats
        birth_date
        college
        end_date
        height_feet
        height_inches
        jersey_number
        name_display_first_last
        name_display_last_first
        name_first
        name_full
        name_last
        name_use
        player_id
        position_txt
        primary_position
        pro_debut_date
        start_date
        starter_sw
        status_code
        team_abbrev
        team_code
        team_id
        team_name
        throws
        weight
    """
    pass


def standings(date):
    DIVISIONS = {
        'AL': {
            '201': 'AL East',
            '202': 'AL Central',
            '200': 'AL West',
        },
        'NL': {
            '204': 'NL East',
            '205': 'NL Central',
            '203': 'NL West',
        }
    }
    now = datetime.now()
    divisions = []
    if date.year == now.year and \
       date.month == now.month and \
       date.day == now.day:
        data = mlbgame.data.get_standings(date)
        standings_schedule_date = 'standings_schedule_date'
    else:
        data = mlbgame.data.get_historical_standings(date)
        standings_schedule_date = 'historical_standings_schedule_date'
    parsed = json.loads(data.decode('utf-8'))
    all_date_rptr = 'standings_all_date_rptr'
    all_date = 'standings_all_date'
    sjson = parsed[standings_schedule_date][all_date_rptr][all_date]
    for league in sjson:
        if league['league_id'] == '103':
            divs = DIVISIONS['AL']
        elif league['league_id'] == '104':
            divs = DIVISIONS['NL']
        for division in divs:
            teams = [team for team in league['queryResults']
                     ['row'] if team['division_id'] == division]
            divisions.append({
                'division': divs[division],
                'teams': teams
            })
    return {
        'standings_schedule_date': standings_schedule_date,
        'divisions': divisions,
    }


class Standings(object):
    """Holds information about the league standings

    Properties:
        divisions
        standings_schedule_date
    """

    def __init__(self, data):
        """Creates a standings object for info specified in `data`.

        `data` should be a dictionary of values
        """
        self.standings_schedule_date = data['standings_schedule_date']
        self.divisions = [Division(x['division'],
                          x['teams']) for x in data['divisions']]


class Division(object):
    """Represents an MLB Division in the standings

    Properties:
        name
        teams
    """

    def __init__(self, name, teams):
        self.name = name
        self.teams = []
        for team in teams:
            self.teams.append(Team(team))


class Team(mlbgame.object.Object):
    """Represents an MLB team in the standings

    Properties:
        away
        clinched_sw
        division
        division_champ
        division_id
        division_odds
        elim
        elim_wildcard
        extra_inn
        file_code
        gb
        gb_wildcard
        home
        interleague
        is_wildcard_sw
        l
        last_ten
        one_run
        opp_runs
        pct
        place
        playoff_odds
        playoff_points_sw
        playoffs_flag_milb
        playoffs_flag_mlb
        playoffs_sw
        points
        runs
        sit_code
        streak
        team_abbrev
        team_full
        team_id
        team_short
        vs_central
        vs_division
        vs_east
        vs_left
        vs_right
        vs_west
        w
        wild_card
        wildcard_odds
        x_wl
        x_wl_seas
    """
    pass


def injury():
    data = mlbgame.data.get_injuries()
    parsed = json.loads(data.decode('utf-8'))
    return parsed['wsfb_news_injury']['queryResults']['row']


class Injuries(object):
    """Represents the MLB Disabled List

    Properties:
        injuries
    """

    def __init__(self, injuries):
        """Creates an Injuries object for given data.

        `injuries` should be a list of injuries.
        """
        self.injuries = [Injury(x) for x in injuries]


class Injury(mlbgame.object.Object):
    """Represents an MLB injury

    Properties:
        display_ts
        due_back
        injury_desc
        injury_status
        injury_update
        insert_ts
        league_id
        name_first
        name_last
        player_id
        position
        team_id
        team_name
    """
    pass
