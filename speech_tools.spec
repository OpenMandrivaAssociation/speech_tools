%define name	speech_tools
%define version	1.2.96
%define release	%mkrel 5

%define major 1
%define libname %mklibname %name %major
%define libnamedevel %mklibname %name -d

%global shared 1
%if !%shared
%define libnamedevel %mklibname -d -s %name
%endif
# some programs may depend on data in */lib only
%define speechtoolsdir %{_prefix}/lib/%{name}

Summary: 	A free speech synthesizer 
Name:  		%{name}
Version: 	%{version}
Release: 	%{release}
License: 	BSD
Group: 		Sound
URL: 		http://www.cstr.ed.ac.uk/projects/festival/
Source0:	speech_tools-%{version}-beta.tar.bz2
Patch1:		speech_tools-1.2.96-gcc41-amd64-int-pointer.patch
Patch2:		speech_tools-1.2.96-remove-invalid-gcc-option.patch
# (fc) 1.2.96-4mdv cxx is not gcc (Fedora)
Patch3:		speech_tools-1.2.96-ohjeezcxxisnotgcc.patch
# (fc) 1.2.96-4mdv build esound module (Fedora)
Patch4:		speech_tools-1.2.96-buildesdmodule.patch
# (fc) 1.2.96-4mdv Fix a coding error (RH bug #162137) (Fedora)
Patch5:		speech_tools-1.2.96-rateconvtrivialbug.patch
# (fc) 1.2.96-4mdv Link libs with libm, libtermcap, and libesd (RH bug #198190) (Fedora)
Patch6:		speech_tools-1.2.96-linklibswithotherlibs.patch
# (fc) 1.2.96-5mdv improve soname (Fedora)
Patch7:		speech_tools-1.2.96-bettersoname.patch
BuildRequires:	ncurses-devel esound-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-root 

%description
Festival is a general multi-lingual speech synthesis system developed
at CSTR. It offers a full text to speech system with various APIs, as
well as an environment for development and research of speech synthesis
techniques. It is written in C++ with a Scheme-based command interpreter
for general control.

%if %shared
%package -n	%{libname}
Summary:  	Static libraries and headers for festival text to speech
Group: 		System/Libraries
Requires: 	%{name} = %{version}-%{release}

%description -n	%{libname}
Festival is a general multi-lingual speech synthesis system developed
at CSTR. It offers a full text to speech system with various APIs, as
well as an environment for development and research of speech synthesis
techniques. It is written in C++ with a Scheme-based command interpreter
for general control.

This package contains the libraries and includes files necessary for
applications that use festival.
%endif

%package -n	%{libnamedevel}
Summary:  	Static libraries and headers for festival text to speech
Group: 		Development/C++
Requires: 	%{name} = %{version}-%{release}
Requires: 	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
%if %shared
Obsoletes:	%mklibname -d %name %major
Obsoletes:	%mklibname -d -s %name
%else
Obsoletes:	%mklibname -d -s %name %major
%endif

%description -n	%{libnamedevel}
Festival is a general multi-lingual speech synthesis system developed
at CSTR. It offers a full text to speech system with various APIs, as
well as an environment for development and research of speech synthesis
techniques. It is written in C++ with a Scheme-based command interpreter
for general control.

This package contains the libraries and includes files necessary to develop
applications using festival.
 
%prep
%setup -q -n %{name}
%patch1 -p1 -b .gcc41-amd64-int-pointer
%patch2 -p0 -b .remove-invalid-gcc-option
%patch3 -p1 -b .cxxisnotgcc
%patch4 -p1 -b .buildesdmodule
%patch5 -p1 -b .rateconvtrivialbug
%patch6 -p1 -b .linklibswithotherlibs
%patch7 -p1 -b .bettersoname

%build
%if shared
export SHARED=2
%endif
%configure2_5x
  # -fPIC 'cause we're building shared libraries and it doesn't hurt
  # -fno-strict-aliasing because of a couple of warnings about code
  #   problems; if $RPM_OPT_FLAGS contains -O2 or above, this puts
  #   it back. Once that problem is gone upstream, remove this for
  #   better optimization.

make \
    CFLAGS="$RPM_OPT_FLAGS -fPIC -fno-strict-aliasing" \
    CXXFLAGS="$RPM_OPT_FLAGS  -fPIC -fno-strict-aliasing"


%check
# all tests must pass
make test

%install
rm -rf %{buildroot}

install -d %{buildroot}/{%{_bindir},%{_libdir},%{_includedir}/EST,%{_datadir}/%{name}/example_data,%{speechtoolsdir}/{scripts,siod,stats/wagon,grammar/{scfg,wfst}}}

rm -f %{buildroot}%{_bindir}/Makefile

# includes
cp -a include/* %{buildroot}%{_includedir}/EST
find %{buildroot}%{_includedir}/EST -name Makefile -exec rm \{\} \;
for file in `find %{buildroot}%{_includedir}/EST -type f`
do
        sed 's/\"\(.*h\)\"/\<EST\/\1\>/g' $file > $file.tmp
	mv $file.tmp $file
done
sed 's/\<EST\//&rxp\//g' %{buildroot}%{_includedir}/EST/rxp/rxp.h > bzzz
mv bzzz %{buildroot}%{_includedir}/EST/rxp/rxp.h
for i in %{buildroot}%{_includedir}/EST/rxp/*
do
	ln -s %{_includedir}/EST/rxp/`basename $i` %{buildroot}%{_includedir}/EST/`basename $i`
done
ln -s %{_includedir}/EST %{buildroot}%{speechtoolsdir}/include

# libraries
install lib/lib* %{buildroot}%{_libdir}
%if %shared
for i in %{buildroot}%{_libdir}/*.so
do
        rm $i
	ln -s `basename $i*` $i
done
%endif
		
# binaries
install `find bin -type f -perm +1` %{buildroot}%{_bindir}

# scripts
install scripts/{example_to_doc++.prl,make_wagon_desc.sh,resynth.sh,shared_script,shared_setup_prl,shared_setup_sh} \
	%{buildroot}%{speechtoolsdir}/scripts

# example data
install lib/example_data/* %{buildroot}%{_datadir}/%{name}/example_data
rm %{buildroot}%{_datadir}/%{name}/example_data/Makefile

cp -a config %{buildroot}%{speechtoolsdir}
cp -r testsuite %{buildroot}%{speechtoolsdir}
rm %{buildroot}%{speechtoolsdir}/testsuite/*.o
install siod/siod.mak %{buildroot}%{speechtoolsdir}/siod
install lib/siod/*.scm %{buildroot}%{speechtoolsdir}/siod
install stats/ols.mak %{buildroot}%{speechtoolsdir}/stats
install stats/wagon/wagon.mak %{buildroot}%{speechtoolsdir}/stats/wagon
install grammar/scfg/scfg.mak %{buildroot}%{speechtoolsdir}/grammar/scfg
install grammar/wfst/wfst.mak %{buildroot}%{speechtoolsdir}/grammar/wfst

# symlinks into buildtree evil
for i in %{buildroot}%{_bindir}/*; do
	if [ -h "$i" ]; then
    		a=`readlink "$i"`
		rm -f "$i"	
		cp -a "$a" %{buildroot}%{_bindir}/
	fi
done

# Remove some files we don't need
rm -rf %{buildroot}%{_includedir}/speech_tools/win32
rm -f  %{buildroot}%{_datadir}/festival/etc/unknown_RedHatLinux/

find %{buildroot} -type f -size 0 -exec rm -f {} \;

%if %shared
%post -n %{libname}  -p /sbin/ldconfig

%postun -n %{libname}
/sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc INSTALL README
%{_bindir}/*
%{_datadir}/%{name}

%if %shared
%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*
%endif

%files -n %{libnamedevel}
%defattr(-,root,root)
%{_includedir}/EST
%dir %{speechtoolsdir}
%{speechtoolsdir}/*
%if %shared
%{_libdir}/*.so
%endif
%{_libdir}/*.a

#%files -n %{libname}-static-devel
#%defattr(-,root,root)
#%_libdir/*.a
