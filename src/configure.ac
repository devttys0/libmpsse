AC_PREREQ([2.65])
AC_INIT([libmpsse],[1.3],[http://libmpsse.googlecode.com])

AC_CONFIG_SRCDIR([mpsse.c])

AC_PROG_CC
AC_LANG(C)

AC_TYPE_SIZE_T
AC_FUNC_MALLOC

CFLAGS="-Wall -fPIC -fno-strict-aliasing $CFLAGS"

dnl Check to see if the libftdi1 headers have been installed
AC_CHECK_HEADERS([libftdi1/ftdi.h], [LIBFTDI1=1], [LIBFTDI1=""])

dnl If libftdi1 headers were not detected, check for libftdi headers/library
if ! test $LIBFTDI1
then
	AC_CHECK_HEADERS([ftdi.h],[LIBFTDI1=0],[echo "error: missing libftdi header files" && exit 1])
	AC_CHECK_LIB([ftdi],[ftdi_init],[],[echo "error: missing libftdi library" && exit 1],[])
	LDFLAGS="-lftdi $LDFLAGS"
dnl Else check for the libftdi1 library
else
	AC_CHECK_LIB([ftdi1],[ftdi_init],[],[echo "error: missing libftdi1 library" && exit 1],[])
	LDFLAGS="-lftdi1 $LDFLAGS"
fi

dnl OSX specific compiler flags
if test "$(uname)" == "Darwin"
then
	SONAME="-install_name"
	FRAMEWORK="-framework Python"
else
	SONAME="-soname"
	FRAMEWORK=""
fi

cp confdefs.h config.h

AC_SUBST(SONAME, $SONAME)
AC_SUBST(FRAMEWORK, $FRAMEWORK)
AC_SUBST(LIBFTDI1, $LIBFTDI1)
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
