# Volleyball Scheduling
The task is to create a schedule of matches

Matches are 3 teams, all of whom play each other
* Teams must be in the same league (e.g. Mens div 2)

Matches need a venue
* The venue must match one of the teams
    * This is a hard-ish constraint, try as constraint first then relax if needed
    * Hm, we have ~11 venues and ~49 teams. With 3 teams/venue/match, we are constrained on the number of venues

Matches happen on a date
* There's a fixed number of dates (about 26)
    * Some teams are unavailable on some dates
    * Some venues are unavailable on some dates
    * Some dates are completely unavailable.

Each team and venue can be in 0-1 match per date

Each league has a tournament structure: e.g. everyone plays everyone else twice
* Only do "everyone plays everyone else twice", use the existing structures, no need to get creative here.

Juniors are maybe unnecessary. Leave them in for now, take them out later.

Each club (collection of teams) must proportional home matches
Each team should have similar home and non-home matches

Aim to distribute games as evenly as possible across the season for each team (so e.g. not all at the end of season)
* Possibly: aim not to screw one team over also.

I must alternate between gendered (men & women) days and mixed days, but I can choose whether we start with a gendered day or a mixed day.
* Just pick gendered for Oct 6th, then try mixed for Oct 6th ana this month. Could try solving both iteratively
    * This means that I can split the problem in two and solve both separately.

Aim to reduce repetitive games e.g. playing the same team on consecutive dates

Could optimise to reduce travel
* Probably not worth doing

## Outputs
* Long outputs
* Lomo format

## Expected Timeline
* 2025-07-31 Somthing working
* 2025-08-15 use in anger

## Remaining todos
* Lomo format outputs
* Get up to date inputs, run
* Implement league structures for 6,7,8 teams
