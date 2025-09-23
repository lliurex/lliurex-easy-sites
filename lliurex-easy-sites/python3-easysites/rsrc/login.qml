import QtQuick 2.6
import Edupals.N4D.Agent 1.0 as N4DAgent


Rectangle {
    width:  childrenRect.width+5
    height:  childrenRect.height+5
    anchors.centerIn: parent
    color: "#e9e9e9"

    N4DAgent.Login
    {
        showAddress:true
        address:'server'
        showCancel: false
        inGroups:["sudo","admins","teachers"]
        
        /*anchors.centerIn: parent*/
        /*
        onLogged: {
            tunnel.on_ticket(ticket);
        }
	*/
	onLogged: ticket => tunnel.on_ticket(ticket);

	/*
        onAuthenticated: {
            tunnel.on_authenticated(passwd);
        }
	*/
	onAuthenticated: passwd => tunnel.on_authenticated(passwd);
    }
}
