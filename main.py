from mltrace.entities import Component

c = Component('fakename', 'fakedesc', 'shreya')
d = c.to_dictionary()
print(c)
print(Component.from_dictionary(d))
