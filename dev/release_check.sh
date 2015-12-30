#!/bin/bash

# Originally from https://github.com/jmcnamara/XlsxWriter/

function clear {
    printf "\033c"
}

clear
echo "|"
echo "| Pre-release checks."
echo "|"
echo


#############################################################
#
# Run tests.
#
function check_test_status {

    echo
    echo -n "Are all tests passing for all Pythons? [y/N]: "
    read RESPONSE

    if [ "$RESPONSE" != "y" ]; then

        echo -n "    Run all tests now?                 [y/N]: "
        read RESPONSE

        if [ "$RESPONSE" != "y" ]; then
            echo
            echo -e "Please run: make test\n";
            exit 1
        else
            echo "    Running tests...";
            make test
            check_test_status
         fi
    fi
}


#############################################################
#
# Check Changes file is up to date.
#
function check_changefile {
    clear

    echo "Latest change in ChangeLog.rst file: "
    perl -ne '$rev++ if /^Version/; exit if $rev > 1; print "    | $_"' ChangeLog.rst

    echo
    echo -n "Is the Changes file updated? [y/N]: "
    read RESPONSE

    if [ "$RESPONSE" != "y" ]; then
        echo
        echo -e "Please update the Change file to proceed.\n";
        exit 1
    fi
}


#############################################################
#
# Check the versions are up to date.
#
#  Prereq: cpan install Perl::Version
#
function check_versions {

    V_FILES=axiom/axiom.py

    clear
    echo
    echo "Latest file versions: "

    grep -He "[0-9]\.[0-9]\.[0-9]" ${V_FILES} | sed 's/:/ : /g' | sed 's/=/ = /' | awk '{printf "    | %-24s %s\n", $1, $5}'

    echo
    echo -n "Are the versions up to date?   [y/N]: "
    read RESPONSE

    if [ "$RESPONSE" != "y" ]; then
        echo -n "    Update versions?           [y/N]: "
        read RESPONSE

        if [ "$RESPONSE" != "y" ]; then
            echo
            echo -e "Please update the versions to proceed.\n";
            exit 1
        else
            echo "    Updating versions...";
            perl -i dev/update_revison.pl ${V_FILES}
            check_versions
         fi
    fi
}

#############################################################
#
# Run release checks.
#
function check_git_status {
    clear

    echo "Git status: "
    git status | awk '{print "    | ", $0}'

    echo "Git log: "
    git log -2 | awk '{print "    | ", $0}'

    echo "Git tags: "
    git tag -l -n1 | tail -1 | awk '{print "    | ", $0}'

    echo "Git branches: "
    git branch -v | tail -1 | awk '{print "    | ", $0}'

    echo
    echo -n "Is the git status okay? [y/N]: "
    read RESPONSE

    if [ "$RESPONSE" != "y" ]; then
        echo
        echo -e "Please fix git status.\n";

        git tag -l -n1 | tail -1 | perl -lane 'printf "git commit -m \"Prep for release %s\"\ngit tag \"%s\"\n\n", $F[4], $F[0]' | perl dev/update_revison.pl
        exit 1
    fi
}

check_test_status
check_changefile
check_versions
check_git_status


#############################################################
#
# All checks complete.
#
clear
echo
echo "Interface configured [OK]"
echo "Versions updated     [OK]"
echo "Git status           [OK]"
echo
echo "Everything is configured.";
echo

echo -n "Run make dist?: [y/N]: ";
read RESPONSE

if [ "$RESPONSE" == "y" ]; then
    make clean
    make dist
else
    exit 1
fi
