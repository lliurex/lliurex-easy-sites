import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15


Rectangle {
    property alias sitesModel:filterModel.model
    property alias listCount:listSites.count
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent
        RowLayout{
            Layout.alignment:Qt.AlignRight
            spacing:10
            Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter.svg"
                enabled:sitesOptionsStackBridge.enableChangeStatusOptions[2]
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-easy-sites","Click to filter sites by status")
                onClicked:optionsMenu.open();
               
                Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    MenuItem{
                        icon.name:"view-visible.svg"
                        text:i18nd("lliurex-easy-sites","Show visible sites")
                        enabled:{
                            if (sitesOptionsStackBridge.filterStatusValue!="visible"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:sitesOptionsStackBridge.manageStatusFilter("visible")
                    }

                    MenuItem{
                        icon.name:"view-hidden.svg"
                        text:i18nd("lliurex-easy-sites","Show hidden sites")
                        enabled:{
                            if (sitesOptionsStackBridge.filterStatusValue!="hidden"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:sitesOptionsStackBridge.manageStatusFilter("hidden")
                    }
                    MenuItem{
                        icon.name:"kt-remove-filters.svg"
                        text:i18nd("lliurex-easy-sites","Remove filter")
                        enabled:{
                            if (sitesOptionsStackBridge.filterStatusValue!="all"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:sitesOptionsStackBridge.manageStatusFilter("all")
                    }
                }
                
            }
             
            PC3.TextField{
                id:siteSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                visible:true
                enabled:{
                    if ((listSites.count==0)&& (text.length==0)) {
                        false
                    }else{
                        true
                    }
                }
                placeholderText:i18nd("lliurex-easy-sites","Search...")
                onTextChanged:{
                    filterModel.update()
                }
                
            }
        }

        Rectangle {

            id:sitesTable
            visible: true
            Layout.fillHeight:true
            Layout.fillWidth:true
            color:"white"
            border.color: "#d3d3d3"


            PC3.ScrollView{
                implicitWidth:parent.width
                implicitHeight:parent.height
                anchors.leftMargin:10

                ListView{
                    id: listSites
                    anchors.fill:parent
                    height: parent.height
                    enabled:true
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:FilterDelegateModel{
                        id:filterModel
                        model:sitesModel
                        role:"name"
                        search:siteSearchEntry.text.trim()
                        statusFilter:sitesOptionsStackBridge.filterStatusValue

                        delegate: ListDelegateSiteItem{
                            width:sitesTable.width
                            siteId:model.id
                            siteImg:model.img
                            siteName:model.name
                            createdBy:model.createdBy
                            updatedBy:model.updatedBy
                            isVisible:model.isVisible
                            siteUrl:model.url
                            siteFolder:model.folder
                        }
                    }
                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (units.largeSpacing * 4)
                        visible: listSites.count==0?true:false
                        text: {
                            if (siteSearchEntry.text.length==0){
                                i18nd("lliurex-easy-sites","No site is configured")
                            }else{
                                i18nd("lliurex-easy-sites","No site found")
                            }
                        }
                    }
                } 
             }
        }
    }
}

