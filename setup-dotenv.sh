# Copy all .env.sample files to .env.docker
for f in $(find . -name .env.sample); do
  cp "$f" "${f%.sample}.docker"
  echo "Copied $f to ${f%.sample}.docker"
done

# Copy all .env.sample.local files to .env
# Useful for running test suites locally that connect to the docker stack
for f in $(find . -name .env.sample.local); do
  cp "$f" "${f%.sample.local}"
  echo "Copied $f to ${f%.sample.local}"
done
