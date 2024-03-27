
with open('thesis.md') as file:
	lines = file.readlines()

	i = 0
	chapter = []
	chapter_title = 'trash'
	readme = []
	for line in lines:
		if line.startswith('='):
			if 'Lab' in chapter_title:
				with open(chapter_title_f + '.md', 'w') as out_file:
					for c_line in chapter:
						out_file.write(c_line)
			chapter_title = lines[i-1].splitlines()[0]
			chapter_title_f = chapter_title.replace(' ', '_').replace(':','')
			if 'Lab' in chapter_title:
				readme.append('['+chapter_title+']('+chapter_title_f+'.md'+')')
			chapter = []
			print(line)
			chapter.append(lines[i-1])
		chapter.append(line)
		i += 1
	print(readme)
	with open('readme.md', 'w') as readme_file:
		for r_line in readme:
			readme_file.write("%s\r\n\r\n" % r_line)

