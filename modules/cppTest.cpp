#include <iostream>

using namespace std;

void cppTest() {
	cout << "This was ran from a CPP file!" << endl;
}

int main(int argc, char* argv[]) {
	if (argc < 2) {
		cout << "Incorrect use!" << endl;
		return 1;
	}
	string command = argv[1];
	if (command == "!cppTest") {
		cppTest();
		return 0;
	}

	cout << "Commands to use: !cppTest" << endl;
	return 0;
}