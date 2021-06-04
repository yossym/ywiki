#!/usr/bin/perl

use lib qw(.);

#エラーのトラップ
#use KCatch qw( execdata );__DATA__
use CGI::Carp qw(fatalsToBrowser);
use strict;

#use warnings;

#時刻の取得
use POSIX 'strftime';

#use Jcode;
use Walrus::YukiWikiDB;
use CGI;
#Markdown 'markdown';
#use Text::Markdown 'markdown';
#use Markdown::TOC;

use Text::MultiMarkdown 'markdown';
#require 'Text/Markdown.pl';
use Cwd;
use Archive::Zip qw( :ERROR_CODES );

my $charset = "utf-8";

my $contenttype = "Content-type:text/html";

my $frontpage       = "FrontPage";
my $frontpage_navi  = $frontpage;
my $append_navi     = "新規";
my $index_navi      = "一覧";
my $search_navi     = "検索";
my $data_setup_navi = "データ管理";

my $akeyl = "accesskey='*'";    #編集
my $akeyr = "accesskey='#'";    #一覧
my $akey0 = "accesskey='0'";    #FrontPage
my $akey5 = "accesskey='5'";    #本文編集
my $akey8 = "accesskey='8'";    #書き込み
my $akey1 = "accesskey='1'";    #検索編集
my $akey2 = "accesskey='2'";    #検索ボタン

#サブタイトル用
my $subtitle = "subtitle";

#ヘルプ用
my $help        = "help";
my $mobile_cols = 80;
my $mobile_rows = 5;

# my $pc_cols = 80;
my $pc_cols = 30;
# my $pc_rows = 10;
my $pc_rows = 4;

my $searchpage = "search";
my $errorpage  = "Error";
my $indexpage  = "Index";

my %form;
my $page;
my %database;
my $database_name = "wiki";
my $motto         = "motto";
my $passwd        = "1122334455";

#CGIのデータ量制限
#$CGI::POST_MAX = 1024 * 1000000;

my $q        = CGI->new();
my $thisurl  = $q->url;
my $editchar = "?";

# for debug
my $debug           = "debug";
my $full_url        = $q->url();
my $server_name     = $q->server_name();
my $server_software = $q->server_software();
my $http            = $q->http();
my $user_agent      = $q->user_agent();
my $mypage;
my $challenge_pswd  = $q->param($motto);
my $postdata        = $q->param('POSTDATA');
my $mycmd           = $q->param('mycmd');
my $searchword      = $q->param('WORD');
my $debug_msg       = "";
my $upload_filename = $q->param('upload_file');
my $backup_dir      = 'backup';

my $bgcolor = "black";
my $color   = "lime";
my $version = '$Id: index.cgi,v 1.22 2016/07/08 23:42:55 yossym Exp yossym $';
my $css     = "css";
my $javascript = "JavaScript";
my $sandbox    = "SandBox";
my $css_msg    = <<EOD;
<!--
    h1 {
//        margin       : 0.5em 10% 1.2em 0px;
    border-style : double; /* 枠の種類 */
        border-width : 0 0 10px;
        border-color : $color;
        font-size    : 200%;
    }

    h2 {
 //       margin       : 0.5em 20% 1.2em 0px;
        border-style : solid;
        border-width : 0 0 5px;
        border-color : lime;
        font-size    : 150%;
    }

    h3 {
//        margin       : 0.9em 30% 0.5em 0px;

        border-style : solid;
        border-width : 0 0 2px;
        border-color : lime;
        font-size    : 100%;
    }

    h4 {
        border-style : dotted;
        border-width : 0 0 5px;
        border-color : lime;
        font-size    : 100%;

    }


    pre{
        border : lime dashed 1px;
 //       margin : 0.9em 10% 0.5em 0px;
        margin: 0% 0% 0% 0%;
        background-color :   #003300 ;
    }

    body
    {
        background-color : black;
        color            : white;
        margin-left      : 4%;
        margin-right     : 4%;
        line-height      : 1.4;
        font-family      : Meiryo, 'メイリオ', sans-serif;
        font-size        : 2em;
line-height:2;
        word-wrap: break-word;
    }

    /* link */
    a
    {
        text-decoration : none;
        color           : lime;
    }

    /* link mouse-over */
    a:hover, a:focus
    {
        color      : black;
        background : lime;
    }

    .body-top
    {
        text-align: left;
    }

    .body-text
    {
        text-align: left;
    }
    .body-btm
    {
        text-align   : right;
        border-style : none;
    }

    /* input */
    input[type=text]{
       /*ここに通常通りCSSで記述*/
        border-color     : lime;
        background-color : black;
        color            : cyan;
        cursor           : pointer;
    }

    /* textarea */
    textarea {
        border-color     : lime;
        background-color : black;
        color            : cyan;
        cursor           : pointer;
        width            : 99%;
        height           : 50%;
        font-size        : 1.5em;
    }

    .tools {
        text-align: right;
    }

    input#submit_search {
        border-color     : black;
        background-color : black;
        color            : lime;
        border-style     : none;
        font-size        : 1em;
    }

    input#submit_write {
        // ここにCSSコードを書く
        border-color     : black;
        background-color : black;
        color            : lime;
        border-style     : none;
        font-size        : 1em;
    }

    .footer {
        text-align       : right;
    }

    .debug {
    color: yellow;
    }


    .toc {
 //       margin       : 0.5em 20% 1.2em 0px;
//        border-style : solid;
//        border-width : 0 0 5px;
        border-color : lime;
        font-size    : 80%;
        background-color :   #003300 ;
    }


-->
EOD

#キャッシュの有効期限=0
#ヒアドキュメント
my $style = <<EOD;
<META http-equiv="Content-Style-Type" content="text/css">
<META http-equiv="Content-Type" content="text/html charset=$charset">
<meta http-equiv="Expires" content="Tue, 20 Aug 1996 14:25:27 GMT">
EOD

# main function call
main();
exit(0);

#------------------------------------------------------------------------------
# main function
#------------------------------------------------------------------------------
sub main
{
    $mypage = $q->param('mypage') || $frontpage_navi;
    $form{mymsg} = $q->param('mymsg');

    unless (tie(%database, "Walrus::YukiWikiDB", $database_name))
    {
        logf("main()", "$database_name is " . $database_name);
        print_error("(dbopen)");
    }

    if ($thisurl =~ /(http|https):/)
    {
        logf("main()", "protcol is http:");
        $debug_msg = "hit";
    }
    else
    {
        logf("main()", "protcol is not http:");
        $thisurl =~ s/included/http/;
    }

    $_ = $mycmd;

    #logf( "main()", '\$cmd is ' . $mycmd );
    logf("main()", '\$cmd is ' . $mypage);

    if (/^read$/)
    {
        logf("main()", "do_read");
        do_read();
    }
    elsif (/^write$/)
    {
        logf("main()", "do_write");
        do_write();
    }
    elsif (/^edit$/)
    {
        logf("main()", "do_edit");
        do_edit();
    }
    elsif (/^index$/)
    {
        logf("main()", "do_index");
        do_index();
    }
    elsif (/^search$/)
    {
        logf("main()", "do_search");
        do_search();
    }
    elsif (/^data_setup$/)
    {
        logf("main()", "do_data_setup");
        do_data_setup();
    }
    elsif (/^backup$/)
    {
        logf("main()", "do_backup");
        do_backup();
    }
    elsif (/^restore$/)
    {
        logf("main()", "do_restore");
        do_restore();
    }
    else
    {
        logf("main()", "default action");
        do_read();
    }

    untie(%database);
}

#------------------------------------------------------------------------------
# htmlヘッダ
#------------------------------------------------------------------------------
sub print_header
{

    my ($title, $editflag) = @_;
    my $tmp = encode($mypage);

    #サブタイトル
    my $st = get_subtitle();

    #PC用
    # すべて小文字で比較
    if ((lc($user_agent) =~ /iphone/))
    {

##	@{[function]}とするとヒアドキュメントなどで関数が使用可能

        print <<EOD;
$contenttype


<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html lang=\"ja\">
<head><title>$title $st</title>
$style
    @{[get_css()]}
    @{[get_javascript()]}
<link rel="index" href="index.cgi">
</head>
<body>

<!-- for PC -->
<div class="tools">
<form method="POST" action="$thisurl">
<input type="text" name="WORD" value="" $akeyl >
<input id="submit_search"  type="submit" value="検索" $akey2 >
<input type="hidden" name="mycmd" value="search" title="検索">
<BR>
<a href=\"$thisurl?mycmd=edit&amp;mypage=$tmp\" $akeyl title="このページを編集 $akeyl">編集</a>
<a href=\"$thisurl\" $akey0 title="FrontPageの表示 $akey0">$frontpage_navi</a>
<a href=\"$thisurl?mycmd=index\" $akeyr title="一覧の表示 $akeyr">$index_navi</a>
<a href=\"$thisurl?mycmd=data_setup\"  title="データのバックアップとリストア ">$data_setup_navi</a>
</form>
</div>
<h1 class="header">$title</h1>
<!-- start of body -->
EOD

    }

    elsif (

           (lc($user_agent) =~ /firefox/)
        or (lc($user_agent) =~ /ipad/)
        or (lc($user_agent) =~ /nexus 7/)
        or (lc($user_agent) =~ /gecko/)
      )
    {

##	@{[function]}とするとヒアドキュメントなどで関数が使用可能

    print <<EOD;
$contenttype


<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html lang=\"ja\">
<head><title>$title $st</title>
$style
    @{[get_css()]}
    @{[get_javascript()]}
<link rel="index" href="index.cgi">
</head>
<body>

<!-- for PC -->
<div class="tools">
<form method="POST" action="$thisurl">
<input type="text" name="WORD" value="" $akeyl >
<input id="submit_search"  type="submit" value="検索" $akey2 >
<input type="hidden" name="mycmd" value="search" title="検索">
<a href=\"$thisurl?mycmd=edit&amp;mypage=$tmp\" $akeyl title="このページを編集 $akeyl">編集</a>
<a href=\"$thisurl\" $akey0 title="FrontPageの表示 $akey0">$frontpage_navi</a>
<a href=\"$thisurl?mycmd=index\" $akeyr title="一覧の表示 $akeyr">$index_navi</a>
<a href=\"$thisurl?mycmd=data_setup\"  title="データのバックアップとリストア ">$data_setup_navi</a>
</form>
</div>
<h1 class="header">$title</h1>
<!-- start of body -->
EOD

    }
    else    #携帯電話
    {
        print <<EOD;
$contenttype


<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html lang=\"ja\">
<head><title>$title $st</title></head>
<body>

<!-- for mobile -->
<h1>$title</h1>
<div>

<form method="POST" action="$thisurl">
    <input type="text" name="WORD" $akey1>
    <input id="submit_search" type="submit" value="検索" $akey2>
    <input type="hidden" name="mycmd" value="search">
</form>

<a href=\"$thisurl?mycmd=edit&amp;mypage=$tmp\" $akeyl>編集</a>
<a href=\"$thisurl\" $akey0>$frontpage_navi</a>
<a href=\"$thisurl?mycmd=index\" $akeyr>$index_navi</a>
</div>
<hr>
<!-- start of body -->
EOD

    }
}

#------------------------------------------------------------------------------
# HTML フッター
#------------------------------------------------------------------------------
sub print_footer
{

    #	@{[function]}とするとヒアドキュメントなどで関数が使用可能

    print <<"EOD";
    <!-- end of body -->
    <div class="footer">
        @{[get_debug()]}
        <HR>
        Version:$version<br>
        <script type="text/javascript">
        document.write("最終更新:" + document.lastModified);

        document.write("<BR>");
        document.write("<BR>");

        document.write(", x:" + window.parent.screen.width);
        document.write(", y:" + window.parent.screen.height);
        document.write("(")
        document.write(", x:" + window.innerWidth);
        document.write(", y:" + window.innerHeight);
        document.write(")")
        </script>
        @{[$mycmd eq "edit" ? @{[get_help()]} : ""]}
    </div>
    </body></html>
EOD
}

#------------------------------------------------------------------------------
# error msg print for browser
#------------------------------------------------------------------------------
sub print_error
{
    my $msg = shift;
    print_header($errorpage, 0);
    print "<h1>$msg</h1>";
    print_footer();
    exit(0);
}

#------------------------------------------------------------------------------
# html body print
#------------------------------------------------------------------------------
sub print_content
{

    # markdown変換
    my $body;

    ($body) = @_;

    # frontpageが存在しない場合に対応
    if (0 < length($body))
    {
        $_ = markdown(shift);
    }
    else
    {
        $_ = markdown("");
    }
    ##	@{[function]}とするとヒアドキュメントなどで関数が使用可能
    # [[]]のキーワードで?と内部リンクを作成する

    s!(\[\[(.*?)\]\])!@{[$database{$2} ?
    qq(<a href="$thisurl?mypage=@{[encode($2)]}" title="内部リンク">$2</a>)
    : qq($2<a href="$thisurl?mycmd=edit&mypage=@{[encode($2)]}"
        title="新しいページを編集" >?</a>)]}!gsm;

    my @lines = split(/\n/, $_);
    my @body;
    my $line;

    #make table of contents
    my $idx = 1;
    my $toc;
    for $line (@lines)
    {

        # toc作成
        if ($line =~ /\<h(\d)\>(.*)\<\/h\d\>/)
        {
            push @body, qq(<h$1><a name='sec$idx'>
        </a>$2<a href='#toc$idx'>&nbsp;&uarr;</a></h$1>\n);

            my $uls = '<ul>' x  ($1);
            my $ule = '</ul>' x ($1);
            $toc = $toc . qq($uls<li><a name='toc$idx'>
        </a><a href='#sec$idx'>$2</a> </li>$ule\n);

            $idx++;

        }
        elsif ($line =~ /\<h(\d)\sid.*\>(.*)\<\/h\d\>/)
        {

            # Text::markdownだと <h1 id="this ">this </h1>の対応
            # toc作成
            push @body, qq(<h$1><a name="sec$idx">
        </a>$2<a href="#toc$idx">&nbsp;&uarr;</a></h$1>\n);
            my $uls = '<ul>' x  ($1);
            my $ule = '</ul>' x ($1);
            $toc = $toc . qq($uls<li><a name="toc$idx">
        </a><a href="#sec$idx">$2</a> </li>$ule\n);
            $idx++;

        }
        else
        {
            push @body, qq($line\r\n);

        }
    }

    #	print $_;
    if (length($toc) > 1)
    {

        print qq(<div class="toc">\n);
        print qq(<h2>目次</h2>\n);
        print $toc;
        print qq(</div>\n);

    }

    $user_agent = $q->user_agent();
    if (lc($user_agent) =~ /iphone/)
    {

        my $lcc = lc($user_agent);
        print qq(<div class="article-text-body">\n);

        print @body;
        print qq(</div><!--  width:900px -->\n);

    }
    else
    {
        print @body;
    }
}

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
sub make_link
{
    $_ = shift;

    print qq(!!!$_!!!);
    if ($database{$_})
    {
        return qq|<a href="$thisurl?$_">$_</a>|;
    }
    else
    {
        return qq|$_<a href="$thisurl?mycmd=edit&mypage=$_">$editchar</a>|;
    }
}

#------------------------------------------------------------------------------
# default print for browser
#------------------------------------------------------------------------------
sub do_read
{
    print_header($mypage, 1);
    print_content($database{$mypage});
    print_footer();
}

#------------------------------------------------------------------------------
# edit content
#------------------------------------------------------------------------------
sub do_edit
{
    print_header($mypage . "の編集中", 0);

    my $mymsg = escape($database{$mypage});

    print <<"EOD";
    <form method="POST" action="$thisurl">
    <div class="body-top">
<!--    合言葉<input type="text" name=$motto > -->
    </div>
    <!-- 文字DoCoMo だったら"$pc_rows"を使用するが、異なったら30行にする -->
    @{[ ($form{user_agent} =~ /DoCoMo/) ?
    qq(<div class="body-text">
        <textarea cols="$mobile_cols" rows="$mobile_rows" name="mymsg"
    $akey5>$mymsg</textarea></div>)
        :
    qq(<!-- pc -->
        <div class="body-text">
        <textarea cols="$pc_cols" rows="$pc_rows" name="mymsg" $akey5 >$mymsg</textarea></div>)
    ]}

    <input type="hidden" name="mycmd" value="write">
    <input type="hidden" name="mypage" value="$mypage">
    <div class="body-btm">
    <input id="submit_write" type="submit"
        value="書込" $akey8 title="このページの書込" >
    </div>
    </form>
EOD

    # 編集中のヘルプ？を印字
    my $pedestal = "keyword = [[$frontpage]], [[$subtitle]],
    [[$help]], [[$debug]], [[$css]], [[$javascript]],
    [[$sandbox]]";
    print_content($pedestal);
    print "<BR>\n";

    print_footer();
}

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
sub do_write
{
    logf("do_write()", $form{mymsg});
    if ($form{mymsg})
    {

        # # passswd is hit.
        # if ($challenge_pswd eq $passwd)
        # {

            logf("do_write()", "passwd hit");
            $database{$mypage} = $form{mymsg};
            print_header($mypage, 1);
            print_content($database{$mypage});
        # }
        # else
        # {
        #     print_header($mypage, 1);
        #     print qq(please input password.);
        # }
    }
    else
    {
        delete $database{$mypage};
        print_header($mypage, 0);
    }
    print_footer();
}

#------------------------------------------------------------------------------
# 値からkeyを求める
#------------------------------------------------------------------------------
sub do_search
{

    print_header($search_navi, 0);

    foreach (sort keys %database)
    {
        my @lines = split(/\n/, $database{$_});
        foreach my $line (@lines)
        {
            if ($line =~ /$searchword/i)
            {
                print qq(<ul>);
                print qq(<li>
                <a href="$thisurl?mypage=@{[encode($_)]}">
                <samp>$_</samp>
                </a>
                </li>);
                print qq($line<br/>);
                print qq(</ul>);
            }
        }

    }
    print_footer();

}

#------------------------------------------------------------------------------
# 一覧を作成
#------------------------------------------------------------------------------
sub do_index
{
    print_header($index_navi, 0);
    print qq|<ul>\n|;
    foreach (sort keys %database)
    {
        print qq|<li><a href="$thisurl?mypage=@{[encode($_)]}">
    <samp>$_</samp></a></li>\n|;

        #読み込んだデータを改行で分割して配列に代入
        my @lines = split(/\n/, $database{$_});
        foreach my $line (@lines)
        {

            # 一行だけ処理
            print_content($line);
            last;
        }
    }
    print qq|</ul>\n|;
    print_footer();
}

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
sub do_backup
{

    if ($challenge_pswd eq $passwd)
    {

        my $zip = Archive::Zip->new();

        # ディレクトリオープン
        opendir(DIRHANDLE, "./wiki");

        # ディレクトリエントリの取得
        foreach (readdir(DIRHANDLE))
        {
            next if /^\.{1,2}$/;    # '.'や'..'をスキップ
            $zip->addFile("./wiki/" . $_);

            #print "$_\n";
        }

        # ディレクトリクローズ
        closedir(DIRHANDLE);

        my $dirname = $backup_dir;

        unless (-d $dirname)
        {
            mkdir $dirname, 0777 or die "$!:$dirname";
        }

        my ($sec, $min, $hour, $mday, $month, $year, $wday, $stime) =
          localtime(time);
        my $zipfile;
        $zipfile = sprintf("%s/pwikidata-%04d%02d%02d_%02d%02d%02d.zip",
                           $dirname, $year + 1900,
                           $month + 1, $mday, $hour, $min, $sec);

        #	my $zipfile = "file.zip";
        my $status = $zip->writeToFileNamed("$zipfile");

        if ($status != 'AZ_OK')
        {
            unlink("$zipfile") if (-e "$zipfile");
            print "Content-Type:text/html\n\n";
            print($zipfile. "が作成されません");
        }

        print "Location: $zipfile\n\n";

    }
    else
    {
        do_data_setup();
    }

}

#------------------------------------------------------------------------------
# wiki dataのリストア
#------------------------------------------------------------------------------
sub do_restore
{

    if ($challenge_pswd eq $passwd)
    {

        logf("do_restore()", "before define");
        my $mytempdir;
        my $buffer;
        my $file;
        my $bytesread;

        logf("do_restore()", "read whie  before $upload_filename ");
        while ($bytesread = read($upload_filename, $buffer, 2048))
        {
            $file .= $buffer;
        }

        logf("do_restore()", "open before $upload_filename");
        my $filename = "./$backup_dir/tmp.zip";
        open(OUT, ">", "$filename") or die("");
        binmode(OUT);
        print(OUT $file);
        close(OUT);

        my $zip = Archive::Zip->new();
        if ($zip->read($filename) == AZ_OK)
        {

            logf("do_restore()", "read after");
            my @members = $zip->members();
            foreach (@members)
            {
                my $fname = $_->fileName;
                logf("do_restore()", "read $fname");
                $zip->extractMember($fname, $fname);
            }
        }

        do_read();

    }
    else
    {
        do_data_setup();
    }

}

#------------------------------------------------------------------------------
# wiki dataのバックアップとリストア
#------------------------------------------------------------------------------
sub do_data_setup
{

    print_header($data_setup_navi, 0);

    print
      qq(<form method="POST" action="$thisurl" ENCTYPE="multipart/form-data" >\n);

    print qq(	<div class="body-top">\n);
    print qq(	合言葉<input type="text" name=$motto >\n);
    print qq(	</div>\n);

    #    print qq(	<input type="hidden" name="mycmd" value="backup">\n);
    print qq(	<div class="body-btm">\n);

    #    print qq(   ファイル名<input type="text" name=$data_filename >\n);
    print qq(   <input type="file" name="upload_file" />\n);

    #    print qq(	<input id="submit_send" type="submit" \n);
    print qq(	<input name="mycmd" type="submit" \n);
    print
      qq(	    value="restore" $akey8 title="wikiデータの送信" ><BR>\n);

    #    print qq(	<input id="submit_recv" type="submit" \n);
    print qq(	<input name="mycmd" type="submit" \n);
    print qq(	    value="backup" $akey8 title="wikiデータの受信" >\n);
    print qq(	</div>\n);
    print qq(</form>\n);

    print_footer();
}

#------------------------------------------------------------------------------
#「サブタイトル」ページを作ればそれをURLのタイトルに追加する
#------------------------------------------------------------------------------
sub get_subtitle
{

    my $result = '';

    if ($database{$subtitle})
    {
        $result = " " . $database{$subtitle};
    }
    return ($result);
}

sub get_debug
{

    if ($database{$debug})
    {

        print "<!-- debug msg start -->\n";

        my $debugmsg = markdown($database{$debug});

        print qq(<div class="debug">\n);
        print "<HR>";
        print "debug msg <BR>\n";

        print "$debugmsg";
        #
        # CGIスクリプトが参照可能な環境変数を書き出します。
        #
        print "<HR>\n";
        print "環境変数<BR>\n";
        print "<HR>";

        print "<TABLE BORDER=\"1\">\n";
        my $key;
        for $key (sort(keys(%ENV)))
        {
            td_print($key, $ENV{$key});
        }

        td_print("thisurl", $thisurl);
        my $filename = make_filename($mypage);
        td_print("mypage $mypage", $filename);
        td_print("mycmd",          $mycmd);
        td_print("challenge_pswd", $challenge_pswd);
        td_print("postdata",       $postdata);
        td_print("searchword",     $searchword);
        td_print("debug_msg",      $debug_msg);

        print "</TABLE>\n";

        print "</div>\n";
        print "<!-- debug msg end -->\n";

    }

}

sub td_print
{
    my ($key, $value) = @_;

    print "<TR><TD><TT>$key</TT></TD><TD><TT>$value</TT></TD></TR>\n";

}

sub get_help
{

    my $result = "";

    if ($database{$help})
    {
        $result = markdown($database{$help});
    }
    return ($result);
}

sub getnowtime
{

    my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) =
      localtime(time);
    my $result;

    my @weekly = ('日', '月', '火', '水', '木', '金', '土');
    $year += 1900;
    $mon  += 1;

    $result = sprintf("%04d-%02d-%02d(%s) %02d-%02d-%02d",
                      $year, $mon, $mday, $weekly[$wday], $hour, $min, $sec);

    #    return ("$year-$mon-$mday($youbi[$wday]) $hour:$min:$sec");
    return ($result);
}

sub get_css
{
    my $result = $css_msg;
    if ($database{$css})
    {

        $result = <<EOD;
<link rel="stylesheet" href="./wiki/637373.txt">
EOD

    }
    else
    {

        $result = <<EOD;
    <style type="text/css">
    $css_msg
    </style>
EOD
    }
    return ($result);
}

sub get_javascript
{
    my $result = "";
    if ($database{$javascript})
    {
        $result = <<EOD;
<script type="text/javascript">
    <!--
$database{$javascript}
    -->
</script>
EOD
    }

    return ($result);
}

# %82%a0 -> あ
#sub decode {
#	my ($s) = @_;
#	$s =~ tr/+/ /;
#	$s =~ s/%([A-Fa-f0-9][A-Fa-f0-9])/pack("C", hex($1))/eg;
#	return $s;
#}
#
##                 #あ -> %82%a0にする
sub encode
{
    my ($encoded) = @_;
    $encoded =~ s/(\W)/'%' . unpack('H2', $1)/eg;
    return $encoded;
}

sub make_filename
{
    my ($key, $self) = @_;
    my $enkey = uc(unpack("H*", $key));
    return "$enkey.txt";
}

sub escape
{
    my $s = shift;
    $s =~ s|\r\n|\n|g;
    $s =~ s|\r|\n|g;
    $s =~ s|\&|&amp;|g;
    $s =~ s|<|&lt;|g;
    $s =~ s|>|&gt;|g;
    $s =~ s|"|&quot;|g;
    return $s;
}

sub logf
{

    if ($database{$debug})
    {

        my ($level, $message) = @_;
        my ($pkg, $files, $line) = caller;
        my $host    = $ENV{'REMOTE_HOST'} | $ENV{'REMOTE_ADDR'};
        my $logfile = "";

        #    warn sprintf "%04d-%02d-%02dT%02d:%02d:%02d [%s] %s at %s line %d.\n",
        #        $time[5]+1900, $time[4]+1, @time[3,2,1,0],
        #        $level, $message,
        #        $files, $line;

        my ($sec, $min, $hour, $mday, $month, $year, $wday, $stime) =
          localtime(time);

        my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

        my $logmsg = sprintf(
                             "%s %02d %02d:%02d:%02d %s: %s,%s. %s,%s\n",
                             $weekly[$wday], $mday, $hour,
                             $min,           $sec,  $host,
                             $files,         $line, $level,
                             $message
                            );

        my $dirname = 'log';

        unless (-d $dirname)
        {
            mkdir $dirname, 0777 or die "$!:$dirname";
        }

        $logfile = sprintf(
            "./%s/debug-%04d-%02d-%02d.log",

            #Cwd::getcwd(), $dirname,
            $dirname,
            $year + 1900,
            $month + 1, $mday
                          );
        # open(FILE, ">>", "$logfile") or die("Error:$!");
        # print FILE $logmsg;
        # close(FILE);
    }

}

# vim:fenc=utf-8:softtabstop=4:autoindent:shiftwidth=4:
#    vim:tw=0:foldmethod=marker:filetype=perl:
