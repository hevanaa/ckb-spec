Name:           ckb-next
Version:        0.2.7
Release:        0.3.20170219gitb59d179%{?dist}
Summary:        Corsair RGB keyboard driver for Linux and OS X
Group:          Applications/System
License:        GPLv2
URL:            https://github.com/mattanger/ckb-next
Source0:        https://github.com/mattanger/ckb-next/archive/master.tar.gz#/%{name}-%{version}.tar.gz

# Upstream ships third party libraries
Patch0:         0001-ckb-external-quazip.patch
# There is no qt5 of quazip in Epel
Patch1:         0002-ckb-external-quazip-epel.patch
# Use /var/run
Patch2:         0003-ckb-use-var-run.patch

# Upstream provides none of the following files
Source1:        ckb.appdata.xml
Source2:        ckb.1

BuildRequires:  qt5-qtbase-devel >= 5.2.0
%if 0%{?fedora}
BuildRequires: quazip-qt5-devel
BuildRequires:  libgudev-devel
%endif
%if 0%{?rhel}
BuildRequires: 	quazip-devel
BuildRequires:  libgudev1-devel
%endif
BuildRequires:  libappindicator-devel
BuildRequires:  systemd-devel
BuildRequires:  zlib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
%{?systemd_requires}

Requires:       qt5-qtbase >= 5.2.0
Obsoletes:      ckb

%description
ckb-next is an open-source driver for Corsair keyboards and mice. It aims to
bring the features of their proprietary CUE software to the Linux and Mac
operating systems. This project is currently a work in progress, but it already
supports much of the same functionality, including full RGB animations.

%prep
%setup -q -n ckb-next-master
%if 0%{?fedora}
%patch0 -p1
%endif
%if 0%{?rhel}
%patch1 -p1
%endif
%patch2 -p1
sed -e 's|QApplication::applicationDirPath()|"%{_libexecdir}/"|' -i src/ckb/animscript.cpp
sed -e '/^ExecStart/cExecStart=%{_libexecdir}/ckb-daemon' -i service/systemd/ckb-daemon.service

%build
qmake-qt5
make %{?_smp_mflags}

%install
install -D -m 755 bin/ckb %{buildroot}%{_bindir}/ckb
install -D -m 755 bin/ckb-daemon %{buildroot}%{_libexecdir}/ckb-daemon
install -d %{buildroot}%{_libexecdir}/ckb-animations
install -m 755 bin/ckb-animations/* %{buildroot}%{_libexecdir}/ckb-animations
install -m 644 -D usr/ckb.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/ckb.png
install -m 644 -D service/systemd/ckb-daemon.service %{buildroot}%{_unitdir}/ckb-daemon.service
desktop-file-install --dir=%{buildroot}%{_datadir}/applications usr/ckb.desktop
mkdir %{buildroot}%{_sbindir}
ln -sf service %{buildroot}%{_sbindir}/rcckb-daemon
install -Dpm 0644                                                             \
%{SOURCE1} %{buildroot}%{_datadir}/appdata/ckb.appdata.xml
appstream-util                                                                \
validate-relax --nonet %{buildroot}%{_datadir}/appdata/ckb.appdata.xml
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_mandir}/man1/ckb.1

%post
# not in preset
if [  $1 == 1 ]
then
   systemctl enable ckb-daemon.service
   systemctl start ckb-daemon
fi
touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :

%preun
%systemd_preun ckb-daemon.service

%postun
%systemd_postun_with_restart ckb-daemon.service
if [ $1 -eq 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor >&/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root)
%license LICENSE
%doc BUILD.md DAEMON.md FIRMWARE README.md
%{_bindir}/ckb
%{_sbindir}/rcckb-daemon
%{_libexecdir}/ckb-daemon
%{_libexecdir}/ckb-animations
%{_unitdir}/ckb-daemon.service
%{_datadir}/applications/ckb.desktop
%{_datadir}/appdata/ckb.appdata.xml
%{_datadir}/icons/hicolor/*/apps/ckb.png
%{_mandir}/man1/ckb.1*

%changelog
* Thu Mar 2 2017 Johan Heikkila <johan.heikkila@gmail.com>
- Changed package name to ckb-next
* Thu Dec 1 2016 Johan Heikkila <johan.heikkila@gmail.com>
- Created spec file for Fedora based on the Suse spec file
- added appdata file
- added man page
* Thu Aug 25 2016 - aloisio@gmx.com
- Update to version 0.2.6
- Use external quazip only when available
- Replaced ckb-fix-desktop-file.patch with %suse_update_desktop_file
- Replaced ckb-daemon-path.patch and ckb-animations-path.patch with macros \
  for consistency.
* Sun Apr 17 2016 - herbert@graeber-clan.de
- Add hicolor folder, too
* Sun Apr 17 2016 - herbert@graeber-clan.de
- Fix icon folder
* Fri Apr 15 2016 - herbert@graeber-clan.de
- Initial package
- Use /var/run instead of /dev/input for communication with the daemon.
- move the daemon and the animations into the libexec folder
