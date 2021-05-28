FROM python:3.8 AS build

COPY . /
RUN pip3 install -r requirements.txt
RUN pip3 install pyinstaller
RUN pyinstaller --onefile /mthook.py 
FROM debian
COPY --from=build /dist/mthook /
RUN /mthook version
# Default run container without commands
CMD ["tail" "-f", "/dev/null" ]
