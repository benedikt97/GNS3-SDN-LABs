
with open('thesis.md') as file:
	lines = file.readlines()

	i = 0
	chapter = []
	chapter_title = 'trash'
	for line in lines:
		if line.startswith('='):
			with open(chapter_title + '.md', 'w') as out_file:
				    for c_line in chapter:
        				out_file.write(c_line)
			chapter_title = lines[i-1]
			chapter = []
			print(line)
			chapter.append(lines[i-1])
		chapter.append(line)
		i += 1
