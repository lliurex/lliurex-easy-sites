import org.kde.plasma.components as Components
import QtCore
import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Dialogs

Components.ItemDelegate{

    id: listSiteItem
    property string siteId
    property string siteImg
    property string siteName
    property string createdBy
    property string updatedBy
    property bool isVisible
    property string siteUrl
    property string siteFolder
    property string selectedFolderToSync

    enabled:true
    height:95

    Rectangle {
        id:containerItem
        height:visible?90:0
        width:parent.width
        color:"transparent"
        border.color: "transparent"

        Item{
            id: menuItem
            height:visible?90:0
            width:containerItem.width-manageSiteBtn.width

            MouseArea{
                id:mouseAreaItem
                anchors.fill:parent
                hoverEnabled:true
                propagateComposedEvents:true

                onEntered:{
                    if (!optionsMenu.activeFocus){
                        listSites.currentIndex=filterModel.visibleElements.indexOf(index)
                    }
                }

            }
            
            Image{
                id:siteImage
                width:60
                height:60
                fillMode:Image.PreserveAspectFit
                source:siteImg
                anchors.verticalCenter:parent.verticalCenter
                anchors.left:parent.left
                anchors.leftMargin:15
            }
            Column{
                id:siteDescription
                anchors.verticalCenter:parent.verticalCenter
                anchors.left:siteImage.right
                anchors.leftMargin:30
                spacing:10
                width:{
                    if (listSiteItem.ListView.isCurrentItem){
                        parent.width-(siteState.width+manageSiteBtn.width+150)
                    }else{
                        parent.width-(siteState.width+130)
                    }
                }
               
                Text{
                    id:nameText
                    text:siteName
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 12
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

                Text{
                    id:descriptionTest
                    text:i18nd("lliurex-easy-sites","Created by:")+" "+createdBy+" - "+i18nd("lliurex-easy-sites","Updated by:")+ " "+updatedBy
                    font.family:"Quattrocento Sans Bold"
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

            }

            Image{
                id:siteState
                source:isVisible?"/usr/share/icons/breeze/actions/24/view-visible.svg":"/usr/share/icons/breeze/actions/24/view-hidden.svg"
                sourceSize.width:32
                sourceSize.height:32
                anchors.left:siteDescription.right
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:30
            }
            
            Button{
                id:manageSiteBtn
                display:AbstractButton.IconOnly
                icon.name:"configure.svg"
                anchors.leftMargin:15
                anchors.left:siteState.right
                anchors.verticalCenter:parent.verticalCenter
                visible:listSiteItem.ListView.isCurrentItem
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-easy-sites","Click to manage this site")
                onClicked:optionsMenu.open();
                onVisibleChanged:{
                    optionsMenu.close()
                }

                Menu{
                    id:optionsMenu
                    y: manageSiteBtn.height
                    x:-(optionsMenu.width-manageSiteBtn.width/2)

                    MenuItem{
                        icon.name:isVisible?"view-hidden.svg":"view-visible.svg"
                        text:isVisible?i18nd("lliurex-easy-sites","Hide site"):i18nd("lliurex-easy-sites","Show site")
                        onClicked:siteStackBridge.changeSiteStatus([siteId,!isVisible])
                    }
                    MenuItem{
                        icon.name:"folder-html.svg"
                        text:i18nd("lliurex-easy-sites","Open site in browser")
                        onClicked:siteStackBridge.viewSiteInBrowser(siteUrl)
                    }
                    MenuItem{
                        icon.name:"folder-black.svg"
                        text:i18nd("lliurex-easy-sites","Open folder")
                        onClicked:siteStackBridge.openSiteFolder(siteFolder)
                    }
                    MenuItem{
                        icon.name:"folder-sync.svg"
                        text:i18nd("lliurex-easy-sites","Sync new content")
                        onClicked:siteFolderDialog.open()
                    }
                    MenuItem{
                        icon.name:"document-edit.svg"
                        text:i18nd("lliurex-easy-sites","Edit site")
                        onClicked:siteStackBridge.loadSite(siteId)
                    }
                    MenuItem{
                        icon.name:"delete.svg"
                        text:i18nd("lliurex-easy-sites","Delete the site")
                        onClicked:sitesOptionsStackBridge.removeSite([false,siteId])
                    }
                }
            }
        }
    }

    FolderDialog{
        id:siteFolderDialog
        title: "Select a folder"
        currentFolder:{
            if (selectedFolderToSync!=""){
               selectedFolderToSync
            }else{
               StandardPaths.standardLocations(StandardPaths.HomeLocation)[0]
            }
        }
        onAccepted:{
            selectedFolderToSync=""
            var tmpFolder=siteFolderDialog.selectedFolder.toString()
            tmpFolder=tmpFolder.replace(/^(file:\/{2})/,"")
            selectedFolderToSync=tmpFolder
            siteStackBridge.syncSiteContent([siteId,selectedFolderToSync])
        }
      
    }   
}
