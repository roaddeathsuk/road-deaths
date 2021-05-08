#!/usr/bin/perl

use strict;

use CGI qw/:standard *TR *table *td *div *ul *ol *li/;           # load standard CGI routines
# use CGI::Carp 'fatalsToBrowser';
use Data::Dumper;

print header(-type => "text/html", -charset => "utf-8");

print start_html("Hello!");

print div(param('user_name'));

print start_form(-method => 'GET');

print textarea(-name => "user_name", -rows=>40, -cols=>50);


