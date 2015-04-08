def netconf_mount(name, address, port, user, password):
    return '''
    <module xmlns="urn:opendaylight:params:xml:ns:yang:controller:config">
    <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">prefix:sal-netconf-connector</type>
    <name>{name}</name>
    <address xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{address}</address>
     <port xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{port}</port>
     <username xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{user}</username>
     <password xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{password}</password>
     <tcp-only xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">false</tcp-only>
     <event-executor xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
        <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:netty">prefix:netty-event-executor</type>
        <name>global-event-executor</name>
     </event-executor>
     <binding-registry xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
        <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:binding">prefix:binding-broker-osgi-registry</type>
        <name>binding-osgi-broker</name>
     </binding-registry>
     <dom-registry xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
        <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:dom">prefix:dom-broker-osgi-registry</type>
        <name>dom-broker</name>
     </dom-registry>
     <client-dispatcher xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
        <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:config:netconf">prefix:netconf-client-dispatcher</type>
        <name>global-netconf-dispatcher</name>
     </client-dispatcher>
     <processing-executor xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
        <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:threadpool">prefix:threadpool</type>
        <name>global-netconf-processing-executor</name>
     </processing-executor>
    </module>)'''.format(name=name, address=address, port=port, user=user, password=password)