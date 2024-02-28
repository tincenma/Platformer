class Button:
	def __init__(self, image, pos):
		self.image = image
		self.x = pos[0]
		self.y = pos[1]
		self.base_color = (255, 255, 255)
		self.hovering_color = (220, 220, 220)
		self.rect = self.image.get_rect(center=pos)

	def update(self, window):
		window.blit(self.image, self.rect)

	def checkForInput(self, pos):
		if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False
