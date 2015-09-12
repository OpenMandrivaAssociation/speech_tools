%define major 2.1.1
%define libestbase %mklibname estbase %{major}
%define libestools %mklibname estools %{major}

%define stringmajor 1.2
%define libeststring %mklibname eststring %{stringmajor}

%define oldlibname %mklibname speech_tools 1
%define devname %mklibname speech_tools -d

Summary:	A free speech synthesizer 
Name:		speech_tools
Version:	2.1
Release:	15
License:	BSD
Group:		Sound
Url:		http://www.cstr.ed.ac.uk/projects/festival/
Source0:	http://festvox.org/packed/festival/%{version}/%{name}-%{version}-release.tar.gz
Patch3: festival.gcc47.patch
# (fc) 1.2.96-4mdv Fix a coding error (RH bug #162137) (Fedora)
Patch5: festival-1.96-speechtools-rateconvtrivialbug.patch
# (fc) 1.2.96-4mdv Link libs with libm, libtermcap, and libesd (RH bug #198190) (Fedora)
# (ahmad) 2.1-2.mga1 modify this patch so that we don't link against libesd,
# as esound is being phased out of the distro
Patch6:		festival-2.1-speechtools-linklibswithotherlibs.patch
# (fc) 1.2.96-5mdv build speech_tools as shared libraries (Fedora)
Patch8:		festival-1.96-speechtools-shared-build.patch
# (fc) 1.96-5mdv  Build main library as shared, not just speech-tools (Fedora)
Patch11:	festival-1.96-main-shared-build.patch
# (fc) 1.2.96-5mdv improve soname (Fedora)
Patch12:	festival-2.1-bettersonamehack.patch
Patch17:	speech_tools-1.2.96-fix-str-fmt.patch

BuildRequires:	perl
BuildRequires:	pkgconfig(ncurses)

%description
Miscellaneous utilities from the Edinburgh Speech Tools. Unless you have a
specific need for one of these programs, you probably don't need to install
this.

%package -n	%{libestbase}
Summary:	Shared libraries for festival text to speech
Group:		System/Libraries
%rename		%{_lib}speech_tools2.1.1

%description -n	%{libestbase}
This package contains the libraries and includes files necessary for
applications that use %{name}.

%package -n	%{libestools}
Summary:	Shared libraries for festival text to speech
Group:		System/Libraries

%description -n	%{libestools}
This package contains the libraries and includes files necessary for
applications that use %{name}.

%package -n	%{libeststring}
Summary:	Shared libraries for festival text to speech
Group:		System/Libraries

%description -n	%{libeststring}
This package contains the libraries and includes files necessary for
applications that use %{name}.

%package -n	%{devname}
Summary:	Development libraries and headers for %{name}
Group:		Development/C++
#Requires:	%{name} = %{version}-%{release}
Requires:	%{libestbase} = %{version}-%{release}
Requires:	%{libestools} = %{version}-%{release}
Requires:	%{libeststring} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the libraries and includes files necessary to develop
applications using %{name}.
 
%prep
%setup -qn %{name}
%apply_patches

# (gb) lib64 fixes, don't bother with a patch for now
perl -pi -e '/^REQUIRED_LIBRARY_DIR/ and s,/usr/lib,%{_libdir},' config/project.mak

%build
%global optflags %{optflags} -Ofast
# build speech tools (and libraries)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/speech_tools/lib
%configure2_5x \
	--disable-static

make LDFLAGS="%{ldflags}" CFLAGS="%{optflags}" CXXFLAGS="%{optflags}" SHARED_LINKFLAGS="%{ldflags}"

%check
# all tests must pass
#make CFLAGS="$RPM_OPT_FLAGS -fPIC -fno-strict-aliasing" \
#    CXXFLAGS="$RPM_OPT_FLAGS  -fPIC -fno-strict-aliasing" test | grep -v INCORRECT

%install
make INSTALLED_LIB=%{buildroot}%{_libdir} make_installed_lib_shared
# no thanks, static libs.
rm -f %{buildroot}%{_libdir}/*.a

make INSTALLED_BIN=%{buildroot}%{_bindir} make_installed_bin_static
# this list of the useful programs in speech_tools comes from
# upstream developer Alan W. Black; the other stuff is to be removed.
pushd %{buildroot}%{_bindir}
	ls |
	grep -Evw "ch_wave|ch_track|na_play|na_record|wagon|wagon_test" |
	grep -Evw "make_wagon_desc|pitchmark|pm|sig2fv|wfst_build" |
	grep -Evw "wfst_run|wfst_run" |
	xargs rm
popd

pushd include
	for header in $(find . -type f -name \*.h | grep -v win32 ); do
		install -m644 "$header" -D "%{buildroot}%{_includedir}/EST/$header"
	done  
popd

%files
%doc README
%{_bindir}/ch_track
%{_bindir}/ch_wave
%{_bindir}/make_wagon_desc
%{_bindir}/na_play
%{_bindir}/na_record
%{_bindir}/pitchmark
%{_bindir}/pm
%{_bindir}/sig2fv
%{_bindir}/wagon
%{_bindir}/wagon_test
%{_bindir}/wfst_run
%{_bindir}/wfst_build

%files -n %{libestbase}
%{_libdir}/libestbase.so.%{major}*

%files -n %{libestools}
%{_libdir}/libestools.so.%{major}*

%files -n %{libeststring}
%{_libdir}/libeststring.so.%{stringmajor}*

%files -n %{devname}
%{_includedir}/EST
%{_libdir}/libestbase.so
%{_libdir}/libestools.so
%{_libdir}/libeststring.so

