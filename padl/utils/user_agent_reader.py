import xml.etree.cElementTree as etree

xmlDoc = open('useragents.xml', 'r')
xmlDocData = xmlDoc.read()
xmlDocTree = etree.XML(xmlDocData)

f = open('../config/user_agent_list.txt','w')

for ua in xmlDocTree.iter('useragent'):
    f.write(ua.get("useragent")+'\n')


f.close()