from app import db , bcrypt


class Role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False, unique=True)

	# realtion avec Users
	users = db.relationship('User', backref='role', lazy=dynamic)


	def __repr__(self):
		return f'<Role : {self.name} >'

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

	# relation avec role
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

	# gestion du password Crypter

	def encrypt_password(self,password):
		hashed = bcrypt.genarate_password_hash(password)
		self.password = hashed.decode('utf-8')

	def verificate_password(self,password)
		return bcrypt.check_password_hash(self.password,password)

	def __repr__(self):
		return f'< User : {self.email} >'

class Profile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String)
	bio = db.Column(db.Text, nullable=False)
	skills = db.Column(db.String(255), nullable=True)
	is_freelance = db.Column(db.Boolean , default=False)

	# Relation avec user
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

	# relation bidirectionel

	user = db.relationship('User', backref=db.backref('Profile', uselist=False))

	def __repr__(self):
		return f'< Profile : {self.first_name} {self.last_name} >' 
