# Rallybook

Rallybook lets the members of a small tennis club book the club's courts from their phone or
computer, instead of writing their names on the paper sheet pinned up in the clubhouse. It is
for volunteer-run clubs in the UK with between 1 and 12 courts. Each club has one or more
admins, usually the club secretary, who look after the club's members and courts.

## Who uses it

- **Members** book courts for themselves and cancel their own bookings.
- **Admins** are members who also manage the club: they invite and remove members and look
  after the courts.

## What it does

- Members see which slots on each court are free or taken, and book and cancel slots.
- Admins invite new members by email and manage the club's membership.

## Product constraints

- Only people a club admin has invited have an account, and each account belongs to one club.
  There is no public sign-up, and people who are not members of the club, such as guests or
  visiting players, never get an account.
- Clubs are in the UK, and every date and time in Rallybook is UK local time.
- A club has at most 12 courts.
- Courts are booked in one-hour slots that start on the hour, from 07:00 to 21:00, so the last
  slot of the day ends at 22:00.
- A member may hold at most 3 upcoming bookings at once.
- Bookings open 14 days before the slot starts, so every member has the same chance at a slot;
  nobody, admins included, can book a court further ahead than that.
- Rallybook takes no payments. Membership and any other fees are handled by the club outside
  Rallybook.
- Rallybook contacts people by email only. It never sends text messages.
