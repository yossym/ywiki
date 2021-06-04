package Walrus::YukiWikiDB;

# Walrus::YukiWikiDB is based on Yuki::YukiWikiDB.
# Only 'store' method modified to write data softly.

$Walrus::YukiWikiDB::VERSION = '1.0.2';
my $debug = 1;
my $use_lock = 1;

# Constructor
sub new {
	return shift->TIEHASH(@_);
}

# tying
sub TIEHASH {
	my ($class, $dbname) = @_;
	my $self = {
		dir => $dbname,
		keys => [],
	};
	if (not -d $self->{dir}) {
		if (!mkdir($self->{dir}, 0777)) {
			print "mkdir(" . $self->{dir} . ") fail\n" if ($debug);
			return undef;
		}
	}
	return bless($self, $class);
}

# Store
sub STORE {
	my ($self, $key, $val) = @_;
	my $file = &make_filename($self, $key);
	my $lock = $file.'.lock';
	my $temp = $file.'.temp';
	my $result = undef;
	$self->{$key} = undef;
	# Lock
	if ($use_lock) {
		unless (open( LOCK, ">$lock" )) {
			print "Can't lock $file.";
			return undef;
		}
		flock( LOCK, 2 );
	}
	# Write
	if (open(FILE,">$temp")) {
		binmode(FILE);
		print FILE $val;
		close(FILE);
		if (rename $temp, $file) {
			$self->{$key} = $val;
		} else {
			print "$file overwrite error.";
			unlink $temp;
		}
	} else {
		print "$file create error.";
	}
	# Unlock and return
	if ($use_lock) {
		flock( LOCK, 8 );
		close( LOCK );
		unlink( $lock );
	}
	return $self->{$key};
}

# Fetch
sub FETCH {
	my ($self, $key) = @_;
	my $file = &make_filename($self, $key);
	if (open(FILE, $file)) {
		local $/;
		$self->{$key} = <FILE>;
		close(FILE);
	}
	return $self->{$key};
}

# Exists
sub EXISTS {
	my ($self, $key) = @_;
	my $file = &make_filename($self, $key);
	return -e($file);
}

# Delete
sub DELETE {
	my ($self, $key) = @_;
	my $file = &make_filename($self, $key);
	unlink $file;
	return delete $self->{$key};
}

sub FIRSTKEY {
	my ($self) = @_;
	opendir(DIR, $self->{dir}) or die $self->{dir};
	@{$self->{keys}} = grep /\.txt$/, readdir(DIR);
	foreach my $name (@{$self->{keys}}) {
		$name =~ s/\.txt$//;
		$name =~ s/[0-9A-F][0-9A-F]/pack("C", hex($&))/eg;
	}
	return shift @{$self->{keys}};
}

sub NEXTKEY {
	my ($self) = @_;
	return shift @{$self->{keys}};
}

sub make_filename {
	my ($self, $key) = @_;
	my $enkey = uc(unpack("H*", $key));
	return $self->{dir} . "/$enkey.txt";
}

1;
