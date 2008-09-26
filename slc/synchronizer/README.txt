Syncronizer Overview
====================

Synchronizer allows you to transfer archetype objectdata via xmlrpc to 
another plone server. On clientside the current object data is read from the schema 
and sent as mapping to the server. On the server, an object with a given portal type
is created and the data is set on it using process_form.

You can manipulate the way how the data mapping is created by providing a specialized 
IDataExtractor adapter. You can also override the portal_type. Using this tweak 
you can transfer data from one plone server to another where it is not necessary 
that the plone versions are the same, only that there are archetype objects on both ends.

Also it is not necessary that the same content type is present on the server side. It 
is the responsibility of the adapter to make sure that a proper mapping is created. This allows
to use the syncronizer to migrate data from one type to another.

Status
======

Currently synchronizing is supported for one object and its referenced peers and 
its translations. It should be fairly straightforward to implement batched synchronization.

Also currently all content is synchronized into one fixed destination on the 
server side. No structure is maintained. This feature may be added in the future though.



Authors
=======

Wolfgang Thomas - thomas at syslab dot com
Alexander Pilz  - pilz at syslab dot com
