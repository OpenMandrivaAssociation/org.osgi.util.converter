Name:		org.osgi.util.converter
Version:	1.0.9
Release:	1
Summary:	OSGi Converter API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.util.converter/%{version}/org.osgi.util.converter-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.util.converter-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:org.osgi.util.function)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Converter 1.0.9. The companion code converts between types and
uses org.osgi.util.function.Function from the packaged function 1.2.0
API. Versioning annotations are compile-time only. The package version
is 1.0.9. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/util/converter")
names = sorted(path.name for path in root.glob("*.java"))
expect = [
    "AbstractCollectionDelegate.java",
    "AbstractSpecifying.java",
    "ArrayDelegate.java",
    "CollectionDelegate.java",
    "CollectionSetDelegate.java",
    "ConversionException.java",
    "Converter.java",
    "ConverterBuilder.java",
    "ConverterBuilderImpl.java",
    "ConverterFunction.java",
    "ConverterImpl.java",
    "Converters.java",
    "Converting.java",
    "ConvertingImpl.java",
    "CustomConverterImpl.java",
    "DTOUtil.java",
    "DynamicMapLikeFacade.java",
    "Functioning.java",
    "FunctioningImpl.java",
    "InternalConverter.java",
    "InternalConverting.java",
    "ListDelegate.java",
    "MapDelegate.java",
    "Rule.java",
    "SetDelegate.java",
    "Specifying.java",
    "TargetRule.java",
    "TypeReference.java",
    "TypeRule.java",
    "Util.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
if list(root.rglob("packageinfo")) or list(Path(".").rglob("packageinfo")):
    raise SystemExit("unexpected packageinfo")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.util.converter</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.util.converter</name>
  <description>OSGi Converter.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.util.function</artifactId>
      <version>1.2.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.util.converter</artifactId>",
    "<artifactId>org.osgi.util.function</artifactId>",
    "<version>1.2.0</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<version>1.0.0</version>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.util.converter-%{version}.jar --describe-module org.osgi.util.converter > module-describe.txt
grep -q '^org.osgi.util.converter' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.util.converter-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = zf.namelist()
if any(name.endswith("packageinfo") for name in names):
    raise SystemExit("unexpected packageinfo")
if "org/osgi/util/converter/package-info.class" not in names:
    raise SystemExit("missing package-info.class")
PY

%files -f .mfiles
%doc LICENSE
