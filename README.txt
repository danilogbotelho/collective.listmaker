.. contents::

Introduction
============

This widget tries to reproduce the List Entry View pattern described
at http://www.welie.com/patterns/showPattern.php?patternID=list-entry-view.

Use when
--------

Users are building up a list of items one by one. The items they are
adding are very simple, typically a name of a person or of an item, and
possible one or two extra fields. If the items are complex, typically
consisting of 4 or more fields, this pattern should not be used. This
pattern is particularily good when a lot of data has to be entered
manually. 

How
----

The widget presents a row with widgets (form) and an 'add' button. Pressing
the button will add the item to the total list and clear the form for
the entry of the next item.

The list of items is a table with columns representing the fields in
the items and with one extra column with buttons to delete them or
edit them.

Why
----

The main strength of this pattern is that it reduces the amount of
steps needed in the process of adding items to a list. Normally, users
would first click on the 'add item' button which then shows the entry
form and then confirm the action. This pattern saves one step in the
process and only minimally clutters the interface. 

